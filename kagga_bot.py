#!/usr/bin/env python3
"""
Mastodon Kagga Bot
==================
Posts all 945 Mankutimmana Kagga verses by D.V. Gundappa (DVG)
to a Mastodon account on a configurable schedule.

Each post includes:
  - Kannada verse
  - Roman transliteration
  - English explanation
  - Hashtags

When a post exceeds 500 chars, it splits into a thread:
  Post 1 (below) -> English explanation
  Post 2 (top)   -> Kannada verse + transliteration + tags

Usage:
    python kagga_bot.py              # Start the scheduler
    python kagga_bot.py --post-now   # Post one verse immediately and exit
    python kagga_bot.py --dry-run    # Preview without sending
    python kagga_bot.py --verse N    # Post a specific verse number (1-945)
    python kagga_bot.py --list-themes
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timedelta

try:
    from mastodon import Mastodon, MastodonError
except ImportError:
    print("ERROR: Run:  pip install --user Mastodon.py")
    sys.exit(1)

import config
from kagga_verses import KAGGA_VERSES

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
handlers = [logging.StreamHandler(sys.stdout)]
try:
    handlers.append(logging.FileHandler(config.LOG_FILE, encoding="utf-8"))
except OSError:
    pass

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=handlers,
)
log = logging.getLogger("kagga_bot")

# ---------------------------------------------------------------------------
# Verse lookup
# ---------------------------------------------------------------------------
_BY_NUMBER = {v["number"]: v for v in KAGGA_VERSES}
_BY_THEME  = {}

for _v in KAGGA_VERSES:
    for _t in _v.get("themes", []):
        for _word in _t.split():
            _w = _word.strip().lower()
            if _w:
                _BY_THEME.setdefault(_w, []).append(_v)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def load_state():
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_index": -1, "total_posted": 0}


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Verse selection
# ---------------------------------------------------------------------------

def pick_verse(specific=None, theme=None):
    if specific is not None:
        v = _BY_NUMBER.get(specific)
        if not v:
            log.error("Verse %d not found.", specific)
            sys.exit(1)
        return v

    if theme:
        pool = _BY_THEME.get(theme.lower(), KAGGA_VERSES)
        return random.choice(pool)

    if config.VERSE_ORDER == "random":
        return random.choice(KAGGA_VERSES)

    state    = load_state()
    next_idx = (state["last_index"] + 1) % len(KAGGA_VERSES)
    verse    = KAGGA_VERSES[next_idx]
    state["last_index"]   = next_idx
    state["total_posted"] = state.get("total_posted", 0) + 1
    save_state(state)
    return verse


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def build_tags(verse, short=False):
    if short:
        return "#Kagga #DVG"
    base = ["#Kagga", "#DVG", "#KannadaPoetry", "#MankutimmanaKagga"]
    return " ".join(base)


# ---------------------------------------------------------------------------
# Post composition
# ---------------------------------------------------------------------------

LIMIT = 500


def build_single(verse, short=False):
    """Single post: verse + transliteration + explanation + tags."""
    num   = str(verse.get("number", ""))
    tags  = build_tags(verse, short=short)
    trans = verse.get("transliteration", "").strip()
    expl  = verse.get("explanation", "").strip()
    kv    = verse["verse"].strip()
    parts = []
    if num:
        parts += ["#" + num, ""]
    parts.append(kv)
    if trans:
        parts += ["", trans]
    if expl:
        parts += ["", expl]
    parts += ["", tags]
    return "\n".join(parts)


def build_thread(verse):
    """
    Two-post thread for long posts.
    Post 1 (older, appears below) -> explanation
    Post 2 (newer, appears on top) -> verse + transliteration + tags
    """
    expl  = verse.get("explanation", "").strip()
    num   = str(verse.get("number", ""))
    tags  = build_tags(verse, short=True)
    trans = verse.get("transliteration", "").strip()
    kv    = verse["verse"].strip()

    p1 = ("💡 " + expl) if expl else ""

    p2_parts = []
    if num:
        p2_parts += ["#" + num, ""]
    p2_parts.append(kv)
    if trans:
        p2_parts += ["", trans]
    p2_parts += ["", tags]
    p2 = "\n".join(p2_parts)

    return p1, p2


# ---------------------------------------------------------------------------
# Mastodon client
# ---------------------------------------------------------------------------

def get_client():
    if config.MASTODON_ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        log.error("Set MASTODON_ACCESS_TOKEN in config.py")
        sys.exit(1)
    return Mastodon(
        access_token=config.MASTODON_ACCESS_TOKEN,
        api_base_url=config.MASTODON_INSTANCE_URL,
    )


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------

def post_verse(dry_run=False, specific=None, theme=None):
    verse = pick_verse(specific=specific, theme=theme)
    num   = verse.get("number", "?")

    # Try 1: single post with full tags
    text = build_single(verse, short=False)

    # Try 2: single post with short tags
    if len(text) > LIMIT:
        text = build_single(verse, short=True)

    # Try 3: thread
    thread = len(text) > LIMIT

    if thread:
        p1, p2 = build_thread(verse)
        log.info("-" * 50)
        log.info("Verse #%s  THREAD", num)
        log.info("Post 1 (%d chars):\n%s", len(p1), p1)
        log.info("Post 2 (%d chars):\n%s", len(p2), p2)
    else:
        log.info("-" * 50)
        log.info("Verse #%s  (%d chars):\n%s", num, len(text), text)

    if dry_run or config.DRY_RUN:
        log.info("[DRY RUN] Not posted.")
        return

    try:
        client = get_client()
        if thread:
            s1 = client.status_post(status=p1, visibility=config.POST_VISIBILITY)
            log.info("Posted 1: %s", s1["url"])
            if p2:
                s2 = client.status_post(
                    status=p2,
                    in_reply_to_id=s1["id"],
                    visibility=config.POST_VISIBILITY
                )
                log.info("Posted 2: %s", s2["url"])
        else:
            s = client.status_post(status=text, visibility=config.POST_VISIBILITY)
            log.info("Posted: %s", s["url"])
    except MastodonError as exc:
        log.error("Mastodon error: %s", exc)
    except Exception as exc:
        log.error("Unexpected error: %s", exc)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

def wait_seconds():
    unit  = config.POSTING_INTERVAL_UNIT
    value = config.POSTING_INTERVAL_VALUE
    now   = datetime.now()
    if unit == "minutes":
        return value * 60
    if unit == "hours":
        return value * 3600
    if unit == "days":
        h, m   = map(int, config.SCHEDULED_TIME.split(":"))
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=value)
        return (target - now).total_seconds()
    raise ValueError("POSTING_INTERVAL_UNIT must be: minutes, hours, or days")


def run_scheduler():
    log.info("Kagga Bot starting  %d verses loaded", len(KAGGA_VERSES))
    log.info("Instance : %s", config.MASTODON_INSTANCE_URL)
    log.info("Schedule : every %d %s", config.POSTING_INTERVAL_VALUE, config.POSTING_INTERVAL_UNIT)
    log.info("Order    : %s", config.VERSE_ORDER)
    post_verse()
    while True:
        secs    = wait_seconds()
        next_at = datetime.now() + timedelta(seconds=secs)
        log.info("Next post at %s", next_at.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(secs)
        post_verse()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def list_themes():
    print("\nAvailable themes:")
    for t in sorted(_BY_THEME.keys()):
        print("  %-20s  (%d verses)" % (t, len(_BY_THEME[t])))


def main():
    parser = argparse.ArgumentParser(description="Mastodon Kagga Bot")
    parser.add_argument("--post-now",    action="store_true", help="Post one verse and exit")
    parser.add_argument("--dry-run",     action="store_true", help="Preview without posting")
    parser.add_argument("--verse",       type=int, default=None, help="Post specific verse (1-945)")
    parser.add_argument("--theme",       type=str, default=None, help="Post random verse from theme")
    parser.add_argument("--list-themes", action="store_true",    help="List all themes")
    args = parser.parse_args()

    if args.list_themes:
        list_themes()
    elif args.post_now or args.dry_run or args.verse or args.theme:
        post_verse(dry_run=args.dry_run, specific=args.verse, theme=args.theme)
    else:
        run_scheduler()


if __name__ == "__main__":
    main()

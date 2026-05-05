# Kagga Bot — Kannada Poetry on Mastodon

**A Mastodon bot that posts DVG's Mankutimmana Kagga — 945 verses of Kannada philosophy — twice daily with transliteration and English explanation.**

→ [Live on Mastodon](https://mastodon.social/@browncoolie) · Part of the [Vibe Coding series](https://mrdee.in/vibecoding/vibecoding-007-kannada-poetry-bot/)

---

## What it does

Scrapes all 945 verses of D.V. Gundappa's *Mankutimmana Kagga* from [kagga.org](https://kagga.org), stores them locally, and posts twice daily to Mastodon with Kannada text, transliteration, and English meaning.

## Run the scraper

```bash
pip install requests beautifulsoup4
python scraper.py --resume                          # resume from checkpoint
python scraper.py --start 1 --end 945 --delay 1.5  # full run
```

All 945 verses are already collected in `kagga_verses.py`.

## Files

- `scraper.py` — scrapes kagga.org with checkpoint/resume support
- `kagga_verses.py` — complete verse data (1.9 MB)
- `scraper_checkpoint.json` — checkpoint state for resuming

# 📜 Mankutimmana Kagga Bot

A Mastodon bot that posts all **945 verses** of *Mankutimmana Kagga* (ಮಂಕುತಿಮ್ಮನ ಕಗ್ಗ) by **D.V. Gundappa (DVG)**, with Roman transliteration and English explanation, on a fully configurable schedule.

> *"ಹುಡುಕಾಟವೇ ಜೀವನ, ಸಿಗದಿರುವುದೇ ಸತ್ಯ"*
> The search itself is life; not finding — that is the truth. — DVG

---

## 📸 Sample Post

```
#2

ಜೀವ ಜಡರೂಪ ಪ್ರಪಂಚವನದಾವುದೋ।
ಆವರಿಸಿಕೊಂಡುಮೊಳನೆರೆದುಮಿಹುದಂತೆ॥
ಭಾವಕೊಳಪಡದಂತೆ ಅಳತೆಗಳವಡದಂತೆ।
ಆ ವಿಶೇಷಕೆ ನಮಿಸೊ - ಮಂಕುತಿಮ್ಮ ॥ ೨ ॥

Jeeva jadaroopa prapanchavanadavudo ...

Salute that unique thing that has surrounded and
penetrated every object — living or otherwise.
Neither does it yield to emotions nor can it be measured.

#Kagga #DVG #KannadaPoetry #MankutimmanaKagga
```

---

## 📁 Files

```
kagga-bot/
├── kagga_bot.py      ← Main bot (scheduler + posting logic)
├── kagga_verses.py   ← All 945 verses (Kannada + transliteration + explanation)
├── config.py         ← All settings — edit this first
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/kagga-bot.git
cd kagga-bot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create a Mastodon bot account

1. Sign up on a Mastodon instance — [ioc.exchange](https://mastodon.social) is recommended
2. Go to **Settings → Edit Profile** → check ✅ *"This is a bot account"*
3. Go to **Settings → Development → New Application**
4. Name it `Kagga Bot`, enable scope `write:statuses` only
5. Copy **"Your access token"**

### 4. Configure

Edit `config.py`:

```python
MASTODON_INSTANCE_URL = "https://mastodon.social"
MASTODON_ACCESS_TOKEN = "your_token_here"
```

### 5. Test

```bash
# Preview post without sending
python kagga_bot.py --dry-run

# Test a specific verse
python kagga_bot.py --verse 1 --dry-run

# Send a real test post
python kagga_bot.py --post-now
```

---

## 🚀 Running

```bash
# Start the scheduler (runs forever, posts every 12 hours by default)
python kagga_bot.py

# Post a specific verse
python kagga_bot.py --verse 42 --post-now

# Post a random verse from a theme
python kagga_bot.py --theme Wisdom --post-now

# See all available themes
python kagga_bot.py --list-themes
```

---

## ⏱️ Schedule Configuration

Set in `config.py` or via environment variables:

| Goal | Settings |
|------|----------|
| Every 6 hours | `UNIT="hours"`, `VALUE=6` |
| Twice a day | `UNIT="hours"`, `VALUE=12` |
| Once a day at 8 AM | `UNIT="days"`, `VALUE=1`, `SCHEDULED_TIME="08:00"` |
| Every 30 minutes | `UNIT="minutes"`, `VALUE=30` |

At `VALUE=12` hours, all 945 verses cycle over **~472 days**.

---

## 🧵 Thread behaviour

Mastodon has a 500 character limit. The bot handles this in order:

1. **Single post** with full tags — if ≤ 500 chars, done
2. **Single post** with short tags (`#Kagga #DVG`) — if ≤ 500 chars, done
3. **Thread** — explanation as Post 1 (below), verse + transliteration as Post 2 (appears on top of timeline)

---

## 🌍 Hosting on PythonAnywhere (free)

```bash
# In PythonAnywhere Bash console
mkdir ~/kagga-bot && cd ~/kagga-bot
# Upload all files via the Files tab
pip install --user Mastodon.py

# Test
python kagga_bot.py --dry-run
```

In the **Tasks** tab, add a scheduled task:
```
python /home/yourusername/kagga-bot/kagga_bot.py --post-now
```

> Note: PythonAnywhere free accounts only allow outbound connections to
> whitelisted domains. Upgrade to the Hacker plan ($5/month) for
> unrestricted access to any Mastodon instance.

---

## 🐳 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "kagga_bot.py"]
```

```bash
docker build -t kagga-bot .
docker run -d \
  -e MASTODON_ACCESS_TOKEN="your_token" \
  -e MASTODON_INSTANCE_URL="https://ioc.exchange" \
  -e POSTING_INTERVAL_UNIT="hours" \
  -e POSTING_INTERVAL_VALUE="12" \
  kagga-bot
```

---

## About Mankutimmana Kagga

*Mankutimmana Kagga* (1943) is a philosophical masterwork by **D.V. Gundappa (DVG)**, written in the *shatpadi* metre in Kannada. Its 945 verses explore life, death, fate, suffering, and the mystery of existence through the voice of "Mankutimma" — the dull-witted Timma — a humble narrator confronting the unanswerable questions of human life.

Source: [mankuthimmanakagga.org](https://mankuthimmanakagga.org/en/kaggas) — free public repository.

---

## License

Code: MIT License

Verse content: Source is a free public repository dedicated to preserving DVG's work.

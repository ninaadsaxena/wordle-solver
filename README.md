# 🟩🟨⬛ Wordle Solver & Browser Automation Bot

An information-entropy-based Wordle solver built in Python, featuring automated browser play on the official NYT Wordle game using Playwright.

It offers two distinct candidate strategies:
1. **Local Dictionary Mode**: Uses a static local word list with a fast pre-computed opener.
2. **Datamuse Live API Mode**: Dynamically fetches candidate words live from the Datamuse API based on known letter patterns.

---

## 🚀 Features

- **Automated Browser Player**: Automatically opens Chromium, bypasses cookie/consent modals, types guesses, reads tile colors, and solves Wordle end-to-end.
- **Information Entropy Engine**: Calculates the expected information gain (in bits) for every possible word to pick the optimal next guess.
- **Fast Openers**: Local mode bypasses ~100M initial calculations by starting with the mathematically optimal opener (`CRANE`).
- **Interactive CLI Assist**: Play along manually in your terminal if you prefer playing on a physical device.
- **Benchmarking Tool**: Test the solver's accuracy and average guess count against random answer samples.

---

## 📁 Project Structure

```
wordle-solver/
├── local/                      # Local dictionary solver files
│   ├── main.py                 # CLI assist & benchmark script
│   ├── build_wordlist.py       # Script to generate words.txt
│   ├── words.txt               # 5-letter English wordlist
│   └── requirements-local.txt
├── muse/                       # Live Datamuse API solver files
│   ├── main_datamuse.py        # Live API CLI assist script
│   ├── datamuse_words.py       # Datamuse API fetcher
│   └── requirements-datamuse.txt
├── engine.py                   # Core generic entropy solver engine
├── wordle_rules.py             # Wordle feedback simulation rules (G/Y/B)
├── browser_bot.py              # Playwright browser controller
├── play.py                     # Unified entry point for Playwright automation
├── requirements.txt            # Project dependencies
└── README.md
```

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ninaadsaxena/wordle-solver.git
   cd wordle-solver
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Chromium for Playwright:**
   ```bash
   playwright install chromium
   ```

---

## 🎮 How to Run

### 1. Automated Browser Solver (Playwright Chromium)

Watch the bot open NYT Wordle and solve today's puzzle automatically:

- **Real Daily Mode (Default - Logged-in NYT Account & Persistent Profile):**
  By default, running `play.py` opens Google Chrome with your persistent profile (where your NYT login session, streak, and daily stats are saved):
  ```bash
  python play.py local
  # or
  python play.py datamuse
  ```

- **Reattempt / Testing Mode (Fresh Incognito Window):**
  If you've already completed today's Wordle on your account, or want to practice/test unlimited times on a fresh board, pass `--reattempt` (or `--test` / `-r`):
  ```bash
  python play.py local --reattempt
  # or
  python play.py datamuse --reattempt
  ```

---

### 2. Interactive CLI Assist Mode

Use the solver in your terminal to guide your own manual game on a phone or computer:

- **Local Assistant:**
  ```bash
  python local/main.py assist
  ```

- **Datamuse Assistant:**
  ```bash
  python muse/main_datamuse.py
  ```

*Enter feedback as 5 letters (e.g., `GYBBG` for Green/Yellow/Black/Black/Green).*

---

### 3. Benchmarking Strategy

Evaluate the local strategy performance against a sample of random words:

```bash
python local/main.py benchmark 50
```

---

## 💡 How It Works

The solver evaluates guesses by maximizing **Shannon Entropy** $H(X)$:

$$H(X) = - \sum_{i} P(x_i) \log_2 P(x_i)$$

For each legal guess, it calculates how candidate words would be partitioned across all possible 243 color feedback patterns ($3^5$). The guess that produces the most uniform distribution of pattern groups yields the highest expected information gain (measured in bits).

---

## 🎯 Top Optimal Opening Guesses

To eliminate unnecessary turn 1 calculations (which require evaluating ~100M word pair combinations), both local and Datamuse solvers randomly select an opening guess from a curated list of top 10 mathematically optimal openers:

```python
TOP_OPENERS = [
    "CRANE", "SLATE", "STARE", "ROATE", "RAISE",
    "TRACE", "SNARE", "ARISE", "SALET", "TALER"
]
```

### Mathematical Rationale
1. **Entropy Ranking**: Based on Information Theory research (including Grant Sanderson / 3Blue1Brown and MIT benchmarks), these 10 words yield the highest expected information gain (~5.75 to 5.84 bits) across all ~13,000 legal 5-letter English words.
2. **Optimal Letter Frequencies**: Every word in this list combines the top vowels (`E`, `A`, `I`/`O`) with the highest-frequency consonants (`R`, `S`, `T`, `N`).
3. **Candidate Reduction**: Starting with any of these 10 words instantly reduces the pool of 2,309 official NYT Wordle solution words down to **fewer than 20 candidate words on average** after just a single guess.

| Word | Expected Information Gain | Avg. Candidates Remaining After Turn 1 |
| :--- | :---: | :---: |
| **SALET** | 5.836 bits | ~15 words |
| **TARSE / ROATE** | 5.828 bits | ~16 words |
| **CRANE** | 5.787 bits | ~18 words |
| **TRACE** | 5.786 bits | ~18 words |
| **SLATE** | 5.785 bits | ~18 words |
| **RAISE / ARISE** | 5.778 bits | ~19 words |
| **SNARE** | 5.760 bits | ~20 words |
| **STARE / TALER** | 5.750 bits | ~21 words |

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

- **Using Local Wordlist:**
  ```bash
  python play.py local
  ```

- **Using Live Datamuse API:**
  ```bash
  python play.py datamuse
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

For each legal guess, it calculates how candidate words would be partitioned across all possible 243 color feedback patterns ($3^5$). The guess that produces the most uniform distribution of pattern groups yields the highest expected information gain (bits).

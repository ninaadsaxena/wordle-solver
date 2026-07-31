"""
nyt_browser.py — drives the REAL nytimes.com/games/wordle page with a
real browser, using Playwright, and feeds the results into the same
Engine from engine.py.

Nothing about the solving logic changes. The only thing this file does
differently from wordle_rules.feedback() is where the pattern comes
from: instead of simulating it in Python, we read it off the actual
rendered page after each guess.

SETUP (run locally — this needs real internet + a real browser, which
this sandbox does not have access to):

pip install playwright
playwright install chromium

USAGE:

python nyt_browser.py

CAVEAT: NYT's page markup is not a documented/stable API. The
selectors below are a reasonable starting point based on how the
page has historically been structured, but you should expect to open
devtools (Inspect Element) on the live page and adjust SELECTORS if
something doesn't match. Look specifically at:
- the element wrapping each row of 5 tiles
- the attribute that changes when a tile flips (commonly `data-state`)
- whatever "Play"/"Continue"/close-icon appears on the intro modal
"""

import time
from playwright.sync_api import sync_playwright

from engine import Engine
from wordle_rules import load_words, feedback as sim_feedback  # sim_feedback used only for entropy scoring

WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html"

# Tune these if the live DOM doesn't match. Open devtools on the real
# page and compare before assuming the automation is broken.
TILE_SELECTOR = "[data-testid='tile']"          # one 5x6 grid of these
FLIP_ANIMATION_SECONDS = 0.4                     # per-tile flip delay
STATE_MAP = {"correct": "G", "present": "Y", "absent": "B"}


def dismiss_modals(page):
"""
NYT shows a 'How to Play' modal and sometimes a subscription/login
nudge on first load. Close-icon selectors change occasionally —
this tries a couple of common patterns and ignores failures.
"""
for selector in [
"button[aria-label='Close']",
"[data-testid='icon-close']",
"button:has-text('Continue')",
]:
try:
page.click(selector, timeout=2000)
time.sleep(0.3)
except Exception:
pass  # modal wasn't there — fine, keep going


REJECTED_WORDS_FILE = "rejected_words.txt"


def load_rejected_words():
"""
Words NYT has told us (via the real UI, in a past run) are not
accepted. Persisted across runs since a rejection is permanent —
no point ever guessing that word again on any future puzzle.
"""
try:
return set(open(REJECTED_WORDS_FILE).read().split())
except FileNotFoundError:
return set()


def save_rejected_word(word):
with open(REJECTED_WORDS_FILE, "a") as f:
f.write(word.upper() + "\n")


def type_guess(page, guess):
for letter in guess:
page.keyboard.press(letter.upper())
time.sleep(0.05)
page.keyboard.press("Enter")
# wait for all 5 tiles in this row to finish flipping
time.sleep(FLIP_ANIMATION_SECONDS * 5 + 0.3)


def clear_current_row(page, word_length=5):
"""Backspace out a rejected guess so the row is empty for a retry."""
for _ in range(word_length):
page.keyboard.press("Backspace")
time.sleep(0.05)


def guess_was_rejected(page, row_index):
"""
A rejected guess never flips tiles — they stay in a non-terminal
state (commonly 'tbd' or 'empty') instead of correct/present/absent.
If NONE of the 5 tiles in this row reached a terminal state, treat
it as a rejection rather than a misread.
"""
tiles = page.query_selector_all(TILE_SELECTOR)
row = tiles[row_index * 5:(row_index + 1) * 5]
states = [t.get_attribute("data-state") for t in row]
return not any(s in STATE_MAP for s in states)


def read_current_row_pattern(page, row_index):
"""
Read the tile states for a specific row (0-indexed) and convert
to the engine's "GYB..." pattern format.
"""
tiles = page.query_selector_all(TILE_SELECTOR)
row = tiles[row_index * 5:(row_index + 1) * 5]
pattern = ""
for tile in row:
state = tile.get_attribute("data-state")
pattern += STATE_MAP.get(state, "B")
return pattern


MAX_REJECTIONS_PER_TURN = 5  # safety cap so a bad selector can't infinite-loop


def play():
words = load_words()
rejected = load_rejected_words()
if rejected:
print(f"Excluding {len(rejected)} previously-rejected word(s) from this session.")
valid_guesses = [w for w in words if w.upper() not in rejected]

eng = Engine(candidates=words, valid_guesses=valid_guesses, feedback_fn=sim_feedback)

with sync_playwright() as p:
browser = p.chromium.launch(headless=False)  # headed, so you can watch/debug
page = browser.new_page()
page.goto(WORDLE_URL)
time.sleep(2)
dismiss_modals(page)

for turn in range(6):
pattern = None
for attempt in range(MAX_REJECTIONS_PER_TURN):
guess = eng.best_guess()
print(f"Turn {turn + 1}: guessing {guess}")
type_guess(page, guess)

if guess_was_rejected(page, turn):
print(f"  -> NYT doesn't accept '{guess}' as a word. "
f"Removing it and trying another guess.")
save_rejected_word(guess)
if guess in eng.valid_guesses:
eng.valid_guesses.remove(guess)
if guess in eng.candidates:
eng.candidates.remove(guess)
clear_current_row(page)
continue

pattern = read_current_row_pattern(page, turn)
print(f"  -> read pattern: {pattern}")
break
else:
print("Too many rejected guesses in a row — stopping to avoid "
"looping forever. Check your word list / selectors.")
break

if pattern == "GGGGG":
print(f"Solved in {turn + 1} guesses!")
break

eng.apply_feedback(guess, pattern)
if not eng.candidates:
print("No candidates left — either a tile misread, or the "
"true answer isn't in the word list.")
break
else:
print("Used all 6 guesses without solving.")

time.sleep(5)  # pause so you can see the final board before it closes
browser.close()


if __name__ == "__main__":
play()

"""
wordle_rules.py — the domain adapter for Wordle.

Everything Wordle-specific lives here: the feedback rule and where the
word list comes from. engine.py never imports anything from this file
by name — you hand it this feedback function and this word list as
plain arguments. Swap this whole file out and engine.py works for a
different game unchanged.
"""

from pathlib import Path

GREEN = "G"
YELLOW = "Y"
GRAY = "B"


def load_words(path=None):
    """
    Load the word list from a plain text file (one word per line or
    space-separated).
    """
    if path is None:
        path = Path(__file__).parent / "local" / "words.txt"
        if not path.exists():
            path = Path(__file__).parent / "words.txt"
    text = Path(path).read_text()
    words = text.split()
    return [w.strip().upper() for w in words if len(w.strip()) == 5]


def feedback(guess, answer):
    """
    Simulate Wordle's tile-coloring logic for a single guess.
    Returns a 5-character string like "GYBBG".
    """
    guess = guess.upper()
    answer = answer.upper()
    result = [GRAY] * 5

    # Pool of letters in `answer` not yet claimed by a green match.
    remaining = list(answer)

    # Pass 1: greens
    for i in range(5):
        if guess[i] == answer[i]:
            result[i] = GREEN
            remaining[remaining.index(guess[i])] = None  # claim it

    # Pass 2: yellows / grays
    for i in range(5):
        if result[i] == GREEN:
            continue
        letter = guess[i]
        if letter in remaining:
            result[i] = YELLOW
            remaining[remaining.index(letter)] = None  # consume supply
        else:
            result[i] = GRAY

    return "".join(result)


def pretty(guess, pattern):
    """Render a guess + pattern the way you'd see it on the board."""
    symbols = {GREEN: "🟩", YELLOW: "🟨", GRAY: "⬛"}
    return " ".join(f"{l}{symbols[p]}" for l, p in zip(guess, pattern))

"""
main_datamuse.py — same assist experience as main.py, but with no local
words.txt at all. Candidates are fetched live from Datamuse each turn,
then filtered locally against your full guess history using the same
feedback() rules from wordle_rules.py.

Run:  python main_datamuse.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import Engine
from wordle_rules import feedback as sim_feedback
from datamuse_words import fetch_words_matching_pattern


def build_pattern(history):
    """Turn known green letters (across all past guesses) into a
    Datamuse wildcard pattern like '?RA?E'."""
    pattern = ["?"] * 5
    for guess, fb in history:
        for i, mark in enumerate(fb):
            if mark == "G":
                pattern[i] = guess[i]
    return "".join(pattern)


def assist():
    history = []  # list of (guess, pattern) already played

    for turn in range(1, 7):
        pattern_str = build_pattern(history)
        candidates = fetch_words_matching_pattern(pattern_str)

        # sp= only encodes GREEN letters — still need to enforce every
        # yellow/gray constraint from the full history ourselves.
        for guess, fb in history:
            candidates = [c for c in candidates if sim_feedback(guess, c) == fb]

        if not candidates:
            print("No live candidates satisfy the constraints so far — "
                  "double-check the feedback you entered.")
            return

        eng = Engine(candidates=candidates, valid_guesses=candidates, feedback_fn=sim_feedback)
        guess = eng.best_guess()
        print(f"Turn {turn}: try  ->  {guess}   ({len(candidates)} live candidates)")

        fb = input(
            "Enter the result as 5 letters (G=green, Y=yellow, B=gray), "
            "e.g. GYBBG: "
        ).strip().upper()

        if fb == "GGGGG":
            print(f"\nSolved in {turn} guesses!")
            return

        history.append((guess, fb))

    print("Out of guesses.")


if __name__ == "__main__":
    assist()

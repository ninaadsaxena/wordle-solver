"""
main.py — plug the generic Engine together with the Wordle adapter.

Two modes:
  python main.py assist      -> you play the real game, this suggests guesses
  python main.py benchmark   -> tests the strategy against every word
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import Engine
from wordle_rules import feedback, load_words, pretty


def make_engine():
    words = load_words()
    return Engine(candidates=words, valid_guesses=words, feedback_fn=feedback)


def assist_mode():
    eng = make_engine()
    print(f"Loaded {len(eng.candidates)} words. Let's solve today's Wordle.\n")

    for turn in range(1, 7):
        guess = eng.best_guess()
        print(f"Turn {turn}: try  ->  {guess}")
        pattern = input(
            "Enter the result as 5 letters (G=green, Y=yellow, B=gray), "
            "e.g. GYBBG: "
        ).strip().upper()

        if pattern == "GGGGG":
            print(f"\nSolved in {turn} guesses!")
            return

        eng.apply_feedback(guess, pattern)

        if not eng.candidates:
            print("\nNo words match that feedback — double check what you typed.")
            return
        elif len(eng.candidates) <= 10:
            print(f"  ({len(eng.candidates)} candidates left: {eng.candidates})\n")
        else:
            print(f"  ({len(eng.candidates)} candidates left)\n")

    print("Out of guesses.")


def benchmark_mode():
    import random
    words = load_words()
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    sample = random.sample(words, min(sample_size, len(words)))
    print(f"Benchmarking against {len(sample)} random words out of {len(words)} "
          f"total (pass a number as a 2nd arg to change sample size, "
          f"or a huge number to run the full list — slow).\n")

    opener = make_engine().best_guess()
    print(f"Opening guess: {opener}\n")

    guess_counts = []
    worst = []
    for i, answer in enumerate(sample):
        eng = Engine(candidates=words, valid_guesses=words, feedback_fn=feedback)
        history = eng.solve(answer, max_guesses=10, opening_guess=opener)
        n = len(history)
        guess_counts.append(n)
        if n > 6:
            worst.append((answer, n, history))
        if (i + 1) % 20 == 0:
            print(f"  ...{i + 1}/{len(sample)} done")

    avg = sum(guess_counts) / len(guess_counts)
    max_g = max(guess_counts)
    solved_by_4 = sum(1 for g in guess_counts if g <= 4) / len(guess_counts) * 100

    print("\n--- Results ---")
    print(f"Average guesses: {avg:.3f}")
    print(f"Worst case:      {max_g}")
    print(f"Solved in <=4:   {solved_by_4:.1f}%")
    if worst:
        print(f"\nWords that took >6 guesses ({len(worst)}):")
        for w, n, h in worst[:10]:
            print(f"  {w}: {n} guesses -> {h}")
    else:
        print("\nEvery word solved within 6 guesses.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "assist"
    if mode == "assist":
        assist_mode()
    elif mode == "benchmark":
        benchmark_mode()
    else:
        print("Usage: python main.py [assist|benchmark]")

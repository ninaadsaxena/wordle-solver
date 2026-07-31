import sys
import time
from browser_bot import WordleBot
from engine import Engine
from wordle_rules import feedback as sim_feedback, load_words
from muse.datamuse_words import fetch_words_matching_pattern

def build_pattern(history):
    """Turn known green letters (across all past guesses) into a
    Datamuse wildcard pattern like '?RA?E'."""
    pattern = ["?"] * 5
    for guess, fb in history:
        for i, mark in enumerate(fb):
            if mark == "G":
                pattern[i] = guess[i]
    return "".join(pattern)

def play_local(bot):
    words = load_words()
    eng = Engine(candidates=words, valid_guesses=words, feedback_fn=sim_feedback)
    
    print(f"Loaded {len(eng.candidates)} words. Playing Wordle using local engine...")
    
    for turn in range(6):
        if turn == 0:
            guess = "CRANE"  # Hardcoded optimal starting guess to bypass the ~100M turn 1 calculations
        else:
            guess = eng.best_guess()
            
        print(f"Turn {turn + 1}: Bot guessing {guess}")
        bot.type_guess(guess)
        
        fb = bot.read_feedback(turn)
        print(f"Turn {turn + 1}: Feedback received: {fb}")
        
        if not fb:
            print("Failed to read feedback. Aborting.")
            return

        if fb == "GGGGG":
            print(f"\nSolved in {turn + 1} guesses!")
            return
            
        eng.apply_feedback(guess, fb)
        
        if not eng.candidates:
            print("\nNo words match that feedback.")
            return
        elif len(eng.candidates) <= 10:
            print(f"  ({len(eng.candidates)} candidates left: {eng.candidates})\n")
        else:
            print(f"  ({len(eng.candidates)} candidates left)\n")

    print("Out of guesses.")

def play_datamuse(bot):
    history = []  # list of (guess, pattern) already played
    print("Playing Wordle using datamuse engine...")

    for turn in range(6):
        pattern_str = build_pattern(history)
        candidates = fetch_words_matching_pattern(pattern_str)

        # sp= only encodes GREEN letters — still need to enforce every
        # yellow/gray constraint from the full history ourselves.
        for guess, fb in history:
            candidates = [c for c in candidates if sim_feedback(guess, c) == fb]

        if not candidates:
            print("No live candidates satisfy the constraints so far.")
            return

        eng = Engine(candidates=candidates, valid_guesses=candidates, feedback_fn=sim_feedback)
        guess = eng.best_guess()
        
        print(f"Turn {turn + 1}: Bot guessing {guess} ({len(candidates)} candidates left)")
        bot.type_guess(guess)
        
        fb = bot.read_feedback(turn)
        print(f"Turn {turn + 1}: Feedback received: {fb}")

        if not fb:
            print("Failed to read feedback. Aborting.")
            return
            
        if fb == "GGGGG":
            print(f"\nSolved in {turn + 1} guesses!")
            return

        history.append((guess, fb))

    print("Out of guesses.")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    
    bot = WordleBot(headless=False)
    try:
        bot.start_game()
        if mode == "datamuse":
            play_datamuse(bot)
        else:
            play_local(bot)
        
        print("Game finished. Keeping browser open for 5 seconds...")
        time.sleep(5)
    finally:
        bot.close()

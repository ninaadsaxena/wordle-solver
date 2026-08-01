import random
import sys
import time
from browser_bot import WordleBot
from engine import Engine
from wordle_rules import feedback as sim_feedback, load_words
from muse.datamuse_words import fetch_words_matching_pattern

TOP_OPENERS = [
    "CRANE", "SLATE", "STARE", "ROATE", "RAISE",
    "TRACE", "SNARE", "ARISE", "SALET", "TALER"
]

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
    
    existing_history = bot.get_existing_history()
    if existing_history:
        print(f"Resuming in-progress game! Found {len(existing_history)} existing guess(es):")
        for past_guess, past_fb in existing_history:
            print(f"  Played: {past_guess} -> {past_fb}")
            eng.apply_feedback(past_guess, past_fb)
        print(f"  ({len(eng.candidates)} candidates remaining)\n")

    print(f"Loaded {len(eng.candidates)} words. Playing Wordle using local engine...")
    
    rejected_words = set()
    turn = len(existing_history)
    
    while turn < 6:
        if turn == 0:
            valid_openers = [w for w in TOP_OPENERS if w in eng.candidates and w not in rejected_words]
            guess = random.choice(valid_openers) if valid_openers else eng.best_guess()
        else:
            guess = eng.best_guess()
            
        if not guess:
            print("No valid guesses left.")
            return

        print(f"Turn {turn + 1}: Bot guessing {guess}")
        bot.type_guess(guess)
        
        # Check if Wordle rejected the word (e.g. invalid word shake)
        if bot.is_rejected(turn):
            print(f"Word '{guess}' was not accepted by Wordle! Backspacing and trying another word...")
            bot.clear_row()
            rejected_words.add(guess)
            if guess in eng.candidates:
                eng.candidates.remove(guess)
            if guess in eng.valid_guesses:
                eng.valid_guesses.remove(guess)
            continue
        
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

        turn += 1

    print("Out of guesses.")

def play_datamuse(bot):
    existing_history = bot.get_existing_history()
    history = list(existing_history)
    
    if history:
        print(f"Resuming in-progress game! Found {len(history)} existing guess(es):")
        for past_guess, past_fb in history:
            print(f"  Played: {past_guess} -> {past_fb}")
        print()

    rejected_words = set()
    print("Playing Wordle using datamuse engine...")

    turn = len(history)
    while turn < 6:
        pattern_str = build_pattern(history)
        raw_candidates = fetch_words_matching_pattern(pattern_str)

        # sp= only encodes GREEN letters — still need to enforce every
        # yellow/gray constraint from the full history and filter rejected words
        candidates = [
            c for c in raw_candidates 
            if c not in rejected_words and all(sim_feedback(g, c) == fb for g, fb in history)
        ]

        if not candidates:
            print("No live candidates satisfy the constraints so far.")
            return

        if turn == 0:
            valid_openers = [w for w in TOP_OPENERS if w in candidates]
            if valid_openers:
                guess = random.choice(valid_openers)
            else:
                eng = Engine(candidates=candidates, valid_guesses=candidates, feedback_fn=sim_feedback)
                guess = eng.best_guess()
        else:
            eng = Engine(candidates=candidates, valid_guesses=candidates, feedback_fn=sim_feedback)
            guess = eng.best_guess()

        if not guess:
            print("No valid guesses left.")
            return
        
        print(f"Turn {turn + 1}: Bot guessing {guess} ({len(candidates)} candidates left)")
        bot.type_guess(guess)

        # Check if Wordle rejected the word
        if bot.is_rejected(turn):
            print(f"Word '{guess}' was not accepted by Wordle! Backspacing and trying another word...")
            bot.clear_row()
            rejected_words.add(guess)
            continue

        fb = bot.read_feedback(turn)
        print(f"Turn {turn + 1}: Feedback received: {fb}")

        if not fb:
            print("Failed to read feedback. Aborting.")
            return
            
        if fb == "GGGGG":
            print(f"\nSolved in {turn + 1} guesses!")
            return

        history.append((guess, fb))
        turn += 1

    print("Out of guesses.")

if __name__ == "__main__":
    mode = "local"
    reattempt = False
    
    for arg in sys.argv[1:]:
        if arg.lower() in ["--reattempt", "--test", "-r"]:
            reattempt = True
        elif arg.lower() in ["local", "datamuse"]:
            mode = arg.lower()
    
    bot = WordleBot(headless=False, reattempt=reattempt)
    try:
        bot.start_game()
        
        if not reattempt and bot.is_already_completed():
            print("\n[Notice] Today's Wordle has already been completed on your account!")
            print(f"To practice or reattempt on a fresh board, run with --reattempt:\n  python play.py {mode} --reattempt\n")
        else:
            if mode == "datamuse":
                play_datamuse(bot)
            else:
                play_local(bot)
        
        print("Game finished. Keeping browser open for 5 seconds...")
        time.sleep(5)
    finally:
        bot.close()

"""
engine.py — a generic "guess and narrow down" solver.

This module knows NOTHING about Wordle, letters, or words.
It only knows about:
  - a pool of candidate hypotheses (could be words, numbers, colors...)
  - a pool of legal guesses (often the same as candidates, but not always)
  - a feedback_fn(guess, target) -> pattern, supplied from OUTSIDE

Because feedback_fn and the word pools are passed in as arguments,
this same engine works for Wordle, Mastermind, or any other
"guess -> get a clue -> narrow down" game. Nothing about English
or 5-letter words is hardcoded here.
"""

import math
from collections import Counter


class Engine:
    def __init__(self, candidates, valid_guesses, feedback_fn):
        """
        candidates:     list of possible answers (mutated as we play)
        valid_guesses:  list of things we're allowed to guess
        feedback_fn:    function(guess, target) -> a hashable pattern
                         (e.g. a string like "GYBBG")
        """
        self.candidates = list(candidates)
        self.valid_guesses = list(valid_guesses)
        self.feedback_fn = feedback_fn

    def entropy(self, guess, guess_pool=None):
        """
        Expected information (in bits) gained by playing `guess`,
        given the CURRENT candidate set.
        """
        pool = guess_pool if guess_pool is not None else self.candidates
        pattern_counts = Counter(
            self.feedback_fn(guess, target) for target in pool
        )
        total = len(pool)
        ent = 0.0
        for count in pattern_counts.values():
            p = count / total
            ent -= p * math.log2(p)
        return ent

    def best_guess(self, guess_pool=None, full_pool_threshold=40):
        """
        Pick the guess with the highest expected information gain.
        """
        if len(self.candidates) == 1:
            return self.candidates[0]

        if guess_pool is not None:
            pool = guess_pool
        elif len(self.candidates) <= full_pool_threshold:
            pool = self.candidates
        else:
            pool = self.valid_guesses

        best_word, best_score = None, -1.0
        for guess in pool:
            score = self.entropy(guess)
            if score > best_score:
                best_word, best_score = guess, score
        return best_word

    def apply_feedback(self, guess, pattern):
        """
        Narrow self.candidates down to only those words that WOULD
        have produced this exact pattern if guessed against them.
        """
        self.candidates = [
            c for c in self.candidates
            if self.feedback_fn(guess, c) == pattern
        ]

    def solve(self, target, max_guesses=6, guess_pool=None, opening_guess=None):
        """
        Auto-play against a known target (used for testing/benchmarking).
        Returns the list of guesses made.
        """
        self.candidates = self.candidates  # keep whatever was set by caller
        history = []
        for turn in range(max_guesses):
            if turn == 0 and opening_guess is not None:
                guess = opening_guess
            else:
                guess = self.best_guess(guess_pool)
            history.append(guess)
            if guess == target:
                return history
            pattern = self.feedback_fn(guess, target)
            self.apply_feedback(guess, pattern)
        return history

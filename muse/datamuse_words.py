"""
datamuse_words.py — candidate supplier that queries the Datamuse API.
"""

import requests

DATAMUSE_URL = "https://api.datamuse.com/words"


def fetch_words_matching_pattern(pattern, max_results=1000):
    """
    Query Datamuse's `sp` (spelled like) endpoint.
    pattern should use `?` for unknown single positions and
    real letters for known (green) positions, e.g. "?RA?E".
    """
    resp = requests.get(
        DATAMUSE_URL,
        params={"sp": pattern, "max": max_results},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    return [
        d["word"].upper()
        for d in data
        if len(d["word"]) == 5 and d["word"].isalpha()
    ]

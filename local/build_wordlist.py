"""
build_wordlist.py — download and filter a 5-letter English word list.
"""

from english_words import get_english_words_set

def build():
    words = get_english_words_set(['web2'], lower=True)
    words5 = sorted([w.upper() for w in words if len(w) == 5 and w.isalpha()])
    
    with open("words.txt", "w") as f:
        f.write("\n".join(words5))
    print(f"Wrote {len(words5)} 5-letter words to words.txt")

if __name__ == "__main__":
    build()

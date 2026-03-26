# Lab 3 — Standard data types, loops, functions
# Task 4 — Specific text analysis
# Developer: Shaulouski Stanislau Andreevich | Version: 1.1 | Date: 2026-03-25
from Decorator import repeatable

# The specific text requested by the user
TEXT = ("So she was considering in her own mind, as well as she could, for the hot day "
        "made her feel very sleepy and stupid, whether the pleasure of making a "
        "daisy-chain would be worth the trouble of getting up and picking the daisies, "
        "when suddenly a White Rabbit with pink eyes ran close by her.")


def split_text(text):
    """Splits text into cleaned words."""
    cleaned = text.replace(",", "").replace(".", "")
    return cleaned.split()


def find_longest_word(words):
    """Finds longest word and its 1-based index."""
    longest = max(words, key=len) if words else ""
    index = words.index(longest) + 1 if words else 0
    return longest, index


@repeatable
def main():
    """Main entry point for Task 4."""
    words = split_text(TEXT)
    long_w, pos = find_longest_word(words)

    print(f"\nTotal words: {len(words)}")
    print(f"Longest word: '{long_w}' at position {pos}")
    print("Every odd-position word:", ", ".join(words[::2]))


if __name__ == "__main__":
    main()
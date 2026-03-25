# Lab 3 — Standard data types, loops, functions
# Task 4 — Text analysis (words, longest word, odd words)
# Developer: Stanislav
# Version: 1.0
# Date: 2026-03-25

TEXT = ("So she was considering in her own mind, as well as she could, for the hot day "
        "made her feel very sleepy and stupid, whether the pleasure of making a "
        "daisy-chain would be worth the trouble of getting up and picking the daisies, "
        "when suddenly a White Rabbit with pink eyes ran close by her.")


def split_text(text):
    """
    Splits text into words using spaces and commas.
    No regular expressions allowed.
    """
    cleaned = text.replace(",", "").replace(".", "")
    return cleaned.split()


def count_words(words):
    """
    Returns the number of words in the list.
    """
    return len(words)


def find_longest_word(words):
    """
    Finds the longest word and its index (1-based).
    Returns (word, index).
    """
    longest = ""
    index = 0

    for i, w in enumerate(words):
        if len(w) > len(longest):
            longest = w
            index = i + 1  # 1-based index

    return longest, index


def print_odd_words(words):
    """
    Prints every odd-position word (1st, 3rd, 5th...).
    """
    print("\nOdd-position words:")
    for i in range(0, len(words), 2):  # 0,2,4... → 1st,3rd,5th...
        print(words[i])


def main():
    """
    Main function performing all three subtasks.
    """
    print("\n Text Analysis (Task 4, Variant 26)")
    print("\nOriginal text:\n")
    print(TEXT)

    words = split_text(TEXT)

    # a) number of words
    total = count_words(words)
    print(f"\n(a) Number of words: {total}")

    # b) longest word + its index
    longest, idx = find_longest_word(words)
    print(f"\n(b) Longest word: '{longest}' (position {idx})")

    # c) odd words
    print_odd_words(words)


if __name__ == "__main__":
    main()

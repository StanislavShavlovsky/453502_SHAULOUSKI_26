# Lab 3 — Standard data types, loops, functions
# Task 3 — Count words starting with lowercase letter
# Developer: Stanislav
# Version: 1.0
# Date: 2026-03-24

def read_text(prompt):
    """
    Reads a non-empty text string from user input.
    """
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Input cannot be empty. Please enter some text.")


def count_lowercase_words(text):
    """
    Counts how many words in the given text start with a lowercase letter.

    Parameters:
        text (str): Input text.

    Returns:
        int: Number of words starting with a lowercase letter.
    """
    words = text.split()
    count = 0

    for w in words:
        if w and w[0].islower():   # no regex allowed
            count += 1

    return count


def compute_lowercase_word_count():
    """
    Reads text from user and prints the number of words
    starting with a lowercase letter.
    """
    print("\nEnter your text below:")
    text = read_text("> ")

    result = count_lowercase_words(text)

    print(f"\nWords starting with lowercase letters: {result}")


def main():
    """
    Main function with repeat option.
    """
    while True:
        compute_lowercase_word_count()
        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()

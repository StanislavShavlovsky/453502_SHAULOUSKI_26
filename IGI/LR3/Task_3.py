# Lab 3 — Standard data types, loops, functions
# Task 3 — Count words starting with lowercase letter
# Developer: Shaulouski Stanislau Andreevich | Version: 1.1 | Date: 2026-03-25

def repeatable(func):
    """Decorator for repeating task."""
    def wrapper():
        while True:
            func()
            if input("\nTry another text? (y/n): ").lower() != 'y': break
    return wrapper

def read_text(prompt):
    """Reads non-empty text."""
    while True:
        text = input(prompt).strip()
        if text: return text
        print("Input cannot be empty.")

def count_lowercase_words(text):
    """Counts words starting with lowercase."""
    return sum(1 for w in text.split() if w and w[0].islower())

@repeatable
def main():
    """Main function for Task 3."""
    text = read_text("\nEnter text: ")
    print(f"Lowercase words count: {count_lowercase_words(text)}")

if __name__ == "__main__":
    main()
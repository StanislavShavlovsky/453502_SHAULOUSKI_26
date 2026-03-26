# Lab 3 — Standard data types, loops, functions
# Task 2 — Average of even numbers
# Developer: Shaulouski Stanislau Andreevich | Version: 1.1 | Date: 2026-03-24

from Decorator import repeatable

def read_int(prompt):
    """Reads an integer value with validation."""
    while True:
        try:
            return int(input(prompt))
        except ValueError: print("Invalid input. Enter an integer.")

def compute_even_average():
    """Reads integers until 1, computes average of even ones."""
    total, count = 0, 0
    print("\nEnter integers (finish with 1):")
    while True:
        num = read_int("> ")
        if num == 1: break
        if num % 2 == 0:
            total += num
            count += 1
    if count == 0: print("No even numbers.")
    else: print(f"Average: {total / count:.4f}")

@repeatable
def main():
    """Main function with decorator repeat."""
    compute_even_average()

if __name__ == "__main__":
    main()
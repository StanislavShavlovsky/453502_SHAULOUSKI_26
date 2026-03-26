# Lab 3 — Standard data types, lists, functions
# Task 5 — List processing with dual initialization
# Developer: Shaulouski Stanislau Andreevich | Version: 1.2 | Date: 2026-03-25

import random


def repeatable(func):
    """Decorator for repeating the task (Requirement 11)."""

    def wrapper():
        while True:
            func()
            if input("\nProcess another list? (y/n): ").lower() != 'y': break

    return wrapper


def init_by_generator(n):
    """Requirement 9: Method 1 - Generator."""
    return [round(random.uniform(-10.0, 10.0), 2) for _ in range(n)]


def init_by_input(n):
    """Requirement 9: Method 2 - User Input."""
    lst = []
    for i in range(n):
        while True:
            try:
                lst.append(float(input(f"Element {i + 1}: ")))
                break
            except ValueError:
                print("Enter a real number.")
    return lst


def sum_of_negatives(lst):
    """Calculates sum of negative elements."""
    return sum(x for x in lst if x < 0)


def product_between_min_max(lst):
    """Computes product between min and max indices."""
    if len(lst) < 2: return 0
    idx1, idx2 = lst.index(min(lst)), lst.index(max(lst))
    start, end = min(idx1, idx2), max(idx1, idx2)
    prod = 1
    for i in range(start + 1, end): prod *= lst[i]
    return prod


@repeatable
def main():
    """Main function for Task 5 with Requirement 8 & 9."""
    try:
        n = int(input("\nEnter list size (Req 8): "))
        mode = input("Choose (g)enerator or (m)anual input: ").lower()

        data = init_by_generator(n) if mode == 'g' else init_by_input(n)
        print(f"List: {data}")
        print(f"Sum of negatives: {sum_of_negatives(data):.2f}")
        print(f"Product: {product_between_min_max(data):.2f}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
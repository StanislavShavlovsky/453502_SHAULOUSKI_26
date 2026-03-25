# Lab 3 — Standard data types, lists, functions
# Task 5 — Sum of negative elements and product between min/max
# Developer: Stanislav
# Version: 1.0
# Date: 2026-03-25

def read_float(prompt):
    """
    Reads a float value from user input with validation.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a real number.")


def input_list():
    """
    Reads a list of real numbers from the user.
    """
    while True:
        try:
            n = int(input("Enter number of elements: "))
            if n <= 0:
                print("List size must be positive.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    lst = []
    print("\nEnter list elements:")
    for i in range(n):
        lst.append(read_float(f"Element {i+1}: "))

    return lst


def print_list(lst):
    """
    Prints the list in a readable format.
    """
    print("\nYour list:")
    print(lst)


def sum_of_negatives(lst):
    """
    Returns the sum of all negative elements in the list.
    """
    return sum(x for x in lst if x < 0)


def product_between_min_max(lst):
    """
    Computes the product of elements located between
    the minimum and maximum elements (exclusive).

    If min and max are adjacent — returns 1.
    """
    min_index = lst.index(min(lst))
    max_index = lst.index(max(lst))

    # Determine correct order
    start = min(min_index, max_index)
    end = max(min_index, max_index)

    # No elements between them
    if end - start <= 1:
        return 1

    product = 1
    for i in range(start + 1, end):
        product *= lst[i]

    return product


def main():
    """
    Main function with repeat option.
    """
    while True:
        print("\n Task 5 — List Processing ")

        lst = input_list()
        print_list(lst)

        neg_sum = sum_of_negatives(lst)
        prod = product_between_min_max(lst)

        print(f"\nSum of negative elements: {neg_sum}")
        print(f"Product of elements between min and max: {prod}")

        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()

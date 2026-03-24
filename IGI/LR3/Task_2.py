# Lab 3 — Standard data types, loops, functions
# Task 2 — Average of even numbers
# Developer: Stanislav
# Version: 1.0
# Date: 2026-03-24

def read_int(prompt):
    """
    Reads an integer value from user input with validation.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer.")


def compute_even_average():
    """
    Reads integers until the user enters 1.
    Computes the average of all even numbers entered.
    """

    total = 0      # sum of even numbers
    count = 0      # how many even numbers were entered

    print("\nEnter integers (finish with 1):")

    while True:
        num = read_int("> ")

        if num == 1:
            break

        if num % 2 == 0:   # even number
            total += num
            count += 1

    if count == 0:
        print("\nNo even numbers were entered.")
    else:
        avg = total / count
        print(f"\nAverage of even numbers: {avg:.4f}")


def main():
    """
    Main function with repeat option.
    """
    while True:
        compute_even_average()
        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()

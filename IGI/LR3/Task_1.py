# Lab 3 — Standard data types, functions, modules
# Task 1 — Power series calculation
# Developer: Stanislav
# Version: 1.0
# Date: 2026-03-24

import math

def repeatable(func):
    """
    Decorator that allows repeating the program execution
    without restarting the script.
    """
    def wrapper():
        while True:
            func()
            again = input("\nRun again? (y/n): ").strip().lower()
            if again != "y":
                print("Goodbye!")
                break
    return wrapper


def read_float(prompt):
    """
    Reads a float value from user input with validation.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def compute_ln_series(x, eps, max_iter=500):
    """
    Computes ln((x+1)/(x-1)) using the power series:
    ln((x+1)/(x-1)) = 2 * Σ[ 1 / ((2n+1) * x^(2n+1)) ], |x| > 1

    Returns:
        (approx_value, n_terms, math_value)
    """
    n = 0
    term = 2 / (1 * x)  # first term
    s = term

    while abs(term) > eps and n < max_iter:
        n += 1
        term = 2 / ((2*n + 1) * x**(2*n + 1))
        s += term

    return s, n, math.log((x + 1) / (x - 1))


@repeatable
def main():
    """
    Main interactive function for computing the series.
    """

    print("\n=== Compute ln((x+1)/(x-1)) using power series ===")

    # Input
    x = read_float("Enter x (|x| > 1): ")
    while abs(x) <= 1:
        print("Condition |x| > 1 is required.")
        x = read_float("Enter x (|x| > 1): ")

    eps = read_float("Enter eps (e.g. 0.0001): ")

    # Compute
    fx, n, math_fx = compute_ln_series(x, eps)

    # Output
    print("\nResult:")
    print(f"|    x    |  n  |       F(x)        |    Math F(x)     |   eps   |")
    print(f"| {x:.4f} | {n:3d} | {fx:.10f} | {math_fx:.10f} | {eps} |")


# Entry point
if __name__ == "__main__":
    main()

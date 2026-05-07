# Program: NumPy Matrix Filtering and Dual Median Calculation
# Lab Work: No. 4, Task 5, Variant 26
# Version: 1.4 (English Documentation)
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-22

import numpy as np
import re


# --- MODULE 1: MIXINS ---

class StatsValidatorMixin:
    """Mixin to validate data before statistical calculations."""

    def is_not_empty(self, data):
        """Checks if the provided numpy array is not empty."""
        return data is not None and data.size > 0


# --- MODULE 2: BASE CLASSES (OOP and Inheritance) ---

class BaseProcessor:
    """Base class for data processing to demonstrate inheritance."""

    def __init__(self):
        """Initializes the base processor with a default description."""
        self._description = "Base NumPy Data Processor"

    def get_info(self):
        """Polymorphic method to retrieve processor information."""
        return f"Description: {self._description}"


class MatrixManager(BaseProcessor, StatsValidatorMixin):
    """
    Class for matrix generation and filtering (Variant 26).
    Demonstrates: static attributes, magic methods, properties, and super().
    """
    # Static attribute to track the number of processed matrices
    total_calculations = 0

    def __init__(self, n, m):
        """Initializes matrix A with random integers and sets dimensions."""
        super().__init__()
        self.__n = n  # Encapsulated dimension (Rows)
        self.__m = m  # Encapsulated dimension (Columns)

        # Create matrix A with random integers between -100 and 100
        # Requirements: a.1 (Array creation), a.2 (Random generation)
        self.__matrix_a = np.random.randint(-100, 100, size=(n, m))

        self._description = "Array C Analyzer (Variant 26)"
        MatrixManager.total_calculations += 1

    # Magic method for string representation
    def __str__(self):
        return f"Matrix {self.__n}x{self.__m}, Instance #{self.total_calculations}"

    # Property for safe access to the source matrix
    @property
    def source_matrix(self):
        return self.__matrix_a

    # --- Core Logic for Variant 26 ---

    def filter_elements(self, b_value):
        """
        Finds elements where |x| > B and stores them in array C.
        Requirements: Variant 26, a.3 (Indexing), a.4 (Universal functions)
        """
        # np.abs is a universal function; masking is used for indexing
        mask = np.abs(self.__matrix_a) > b_value
        array_c = self.__matrix_a[mask]
        return array_c

    def calculate_statistics(self, array_c):
        """
        Calculates median in two ways and provides general stats.
        Requirements: b.1 (mean), b.2 (median), b.4 (var), b.5 (std)
        """
        if not self.is_not_empty(array_c):
            print("Array C is empty. Cannot perform calculations.")
            return

        # --- Median: Method 1 (Standard NumPy function) ---
        numpy_median = np.median(array_c)

        # --- Median: Method 2 (Manual calculation via formula) ---
        sorted_c = np.sort(array_c)
        count = len(sorted_c)
        mid = count // 2

        if count % 2 == 0:
            # If even: average of the two middle elements
            manual_median = (sorted_c[mid - 1] + sorted_c[mid]) / 2
        else:
            # If odd: the middle element
            manual_median = sorted_c[mid]

        # Printing results for Task 5 requirements
        print(f"\n--- Statistical Report (Array C) ---")
        print(f"1. Median (NumPy): {numpy_median}")
        print(f"2. Median (Manual Calculation): {manual_median}")
        print(f"3. Mean value: {np.mean(array_c):.2f}")
        print(f"4. Variance (Var): {np.var(array_c):.2f}")
        print(f"5. Standard Deviation (Std): {np.std(array_c):.2f}")

        # Note: corrcoef (b.3) requires at least two variables or rows
        if len(array_c) > 1:
            print(f"6. Correlation Coefficient (Self): {np.corrcoef(array_c)[0, 0]}")


# --- MODULE 3: UTILS (Validation) ---

def safe_input(prompt):
    """
    Requirement 8: Protection from incorrect user input.
    Uses Regular Expressions to validate integer input.
    """
    while True:
        raw = input(prompt).strip()
        # Regex for integers (supports negative signs)
        if re.match(r'^-?\d+$', raw):
            return int(raw)
        print("Input Error! Please enter a valid integer.")


# --- MODULE 4: MAIN ---

def run_iteration():
    """Performs a single cycle of matrix processing."""
    print("\n" + "=" * 40)
    print("TASK 5: NUMPY ANALYSIS (VARIANT 26)")
    print("=" * 40)

    n = safe_input("Enter number of rows (n): ")
    m = safe_input("Enter number of columns (m): ")

    # Object-oriented approach
    manager = MatrixManager(n, m)

    print(f"\nStatus: {manager}")
    print(f"Polymorphic Info: {manager.get_info()}")
    print("Source Matrix A:\n", manager.source_matrix)

    b = safe_input("\nEnter threshold B for filtering (|x| > B): ")

    # Logic execution
    array_c = manager.filter_elements(b)

    print(f"\nArray C (Filtered elements): {array_c}")
    print(f"Count of elements found: {len(array_c)}")

    # Statistics execution
    manager.calculate_statistics(array_c)


def main():
    """Main application loop."""
    while True:
        try:
            run_iteration()
            user_choice = input("\nRun another calculation? (y/n): ").lower()
            if user_choice not in ['y', 'yes', 'д']:
                print("Exiting application...")
                break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
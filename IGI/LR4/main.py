# Program: Main Integration Module for Laboratory Work No. 4
# Lab Work: No. 4 (Tasks 1-6)
# Version: 1.1 (English Documentation)
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-05-07

import re
import sys

def validate_menu_input(prompt):
    """
    Validates menu selection using Regular Expressions.
    Satisfies Requirement #8: Protection against incorrect user data.
    """
    while True:
        user_input = input(prompt).strip()
        # Regex: allows digits from 0 to 6 only
        if re.match(r'^[0-6]$', user_input):
            return int(user_input)
        print("Error! Please enter a number between 1 and 6 (or 0 to Exit).")

def main():
    """
    Central control module for Laboratory Work No. 4.
    Provides a unified interface for all modularized tasks.
    """
    print("=" * 45)
    print("LABORATORY WORK NO. 4 | VARIANT 26")
    print("DEVELOPER: SHAULOUSKI STANISLAU ANDREEVICH")
    print("=" * 45)

    while True:
        print("\n--- TASK LIST ---")
        print("1. Serialization (Advanced Trees)")
        print("2. Text Analysis (Regular Expressions)")
        print("3. Series Calculation (Logarithmic Functions)")
        print("4. Geometry Visualization (Rhombus)")
        print("5. Matrix Operations (NumPy Analysis)")
        print("6. Planetary Dataset Analysis (Pandas)")
        print("0. Exit Application")

        choice = validate_menu_input("\nSelect task number (0-6): ")

        if choice == 0:
            print("\nApplication closed. Have a productive day!")
            break

        try:
            # Dynamic module loading based on user selection
            if choice == 1:
                import Serializer
                Serializer.main()
            elif choice == 2:
                import Text_analyzer
                Text_analyzer.main()
            elif choice == 3:
                import func_calculator
                func_calculator.main()
            elif choice == 4:
                import Shape
                Shape.main()
            elif choice == 5:
                import Matrix
                Matrix.main()
            elif choice == 6:
                import DatasetAnalyzer
                DatasetAnalyzer.main()

        except ImportError as e:
            # Requirement: Logical grouping in modules
            print(f"\n[ERROR]: Module file not found. Check filename: {e}")
        except AttributeError:
            print(f"\n[ERROR]: Entry point 'main()' not found in module {choice}.")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] in Task {choice}: {e}")

        input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()
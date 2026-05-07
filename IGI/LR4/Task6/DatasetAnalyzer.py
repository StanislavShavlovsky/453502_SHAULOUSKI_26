# Program: Exoplanet Data Analysis using real OEC Dataset
# Lab Work: No. 4, Task 6, Variant 26
# Version: 1.3 (English Documentation)
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-05-07

import pandas as pd
import re
import os


# --- MODULE 1: MIXINS ---

class DataReportMixin:
    """Mixin to provide formatted reporting for data analysis steps."""

    def report_step(self, message):
        """Prints a standardized header for each analysis step."""
        print(f"\n[STEP]: {message}")
        print("-" * 30)


# --- MODULE 2: BASE CLASSES ---

class BaseDatasetHandler:
    """Base class for handling datasets and verifying file integrity."""

    def __init__(self, file_path):
        """Initializes the handler with a file path and checks existence."""
        self.file_path = file_path
        self._exists = os.path.exists(file_path)

    def get_info(self):
        """Demonstrates polymorphism: returns file status information."""
        return f"File: {self.file_path} | Found: {self._exists}"


class PlanetaryAnalyzer(BaseDatasetHandler, DataReportMixin):
    """
    Analyzes exoplanet data using Pandas.
    Demonstrates: static attributes, encapsulation, properties, and magic methods.
    """
    # Static attribute (Requirement 4)
    analysis_instances = 0

    def __init__(self, file_path="oec.csv"):
        """Loads the CSV data into a private DataFrame and increments instance counter."""
        super().__init__(file_path)
        if not self._exists:
            raise FileNotFoundError(f"Data file {file_path} not found!")

        # Encapsulation: the raw DataFrame is kept private (Requirement 4)
        self.__df = pd.read_csv(file_path)
        PlanetaryAnalyzer.analysis_instances += 1

    # Magic Method: provides object description (Requirement 4)
    def __str__(self):
        return f"PlanetaryAnalyzer (Rows: {len(self.__df)}, Cols: {len(self.__df.columns)})"

    # Property: safe access to the internal data (Requirement 4)
    @property
    def data(self):
        """Returns the internal Pandas DataFrame."""
        return self.__df

    # --- TASK A: Series, Filtering, and Reindexing ---
    def perform_task_a(self):
        """
        Creates mass_series, filters mass > 1, and reindexes the result.
        Requirements: Pandas Series, .loc/.iloc, Filtering, Reindexing.
        """
        self.report_step("TASK A: Mass Series Filtering (Mass > 1)")

        # 3. Creating a Series (PlanetaryMassJpt values indexed by Planet Identifier)
        mass_series = self.__df.set_index('PlanetIdentifier')['PlanetaryMassJpt']

        # Cleaning: drop NaN values to ensure correct comparison
        mass_series = mass_series.dropna()

        # 5. Accessing/Filtering using boolean indexing
        # Filter: only planets with mass > 1 Jupiter Mass
        filtered_series = mass_series[mass_series > 1]

        # Reindexing: converting the Series back to a clean DataFrame with new index
        reindexed_result = filtered_series.reset_index()

        print(f"Planets with mass > 1 Jpt found: {len(reindexed_result)}")
        # 4. Displaying top results
        print(reindexed_result.head(10))

    # --- TASK B: Statistical Analysis ---
    def perform_task_b(self):
        """
        Calculates ratio of avg periods for max vs min radius planets.
        Requirements: Indexing, max/min extraction, statistical mean.
        """
        self.report_step("TASK B: Orbital Period Statistics (Ratio calculation)")

        # Selecting relevant columns and dropping incomplete rows
        temp_df = self.__df[['RadiusJpt', 'PeriodDays']].dropna()

        if temp_df.empty:
            print("Error: No valid data points found for Radius/Period.")
            return

        # Finding Max and Min values for Radius
        max_r = temp_df['RadiusJpt'].max()
        min_r = temp_df['RadiusJpt'].min()

        # Extracting orbital periods for planets matching these specific radii
        # and calculating the arithmetic mean (Requirement b.1)
        avg_period_max = temp_df[temp_df['RadiusJpt'] == max_r]['PeriodDays'].mean()
        avg_period_min = temp_df[temp_df['RadiusJpt'] == min_r]['PeriodDays'].mean()

        # Final Ratio calculation
        if avg_period_min != 0:
            ratio = avg_period_max / avg_period_min
            print(f"Max Radius: {max_r} Jpt | Avg Period: {avg_period_max:.2f} days")
            print(f"Min Radius: {min_r} Jpt | Avg Period: {avg_period_min:.2f} days")
            print(f"\nRESULT: Period of largest planets is {ratio:.2f}x longer than smallest.")
        else:
            print("Calculation failed: Division by zero (min period is 0).")


# --- MODULE 3: INTERFACE ---

def validate_input(prompt):
    """Ensures menu selection is between 1-3 using Regular Expressions (Requirement 8)."""
    while True:
        choice = input(prompt).strip()
        if re.match(r'^[1-3]$', choice):
            return choice
        print("Invalid entry! Choose a number between 1 and 3.")


def main():
    """Main execution entry point (Requirement 7)."""
    try:
        # Initializing the analyzer (OEC = Open Exoplanet Catalogue)
        analyzer = PlanetaryAnalyzer("oec.csv")

        while True:
            print("\n" + "=" * 45)
            print("EXOPLANET DATA ANALYSIS (VARIANT 26)")
            print("=" * 45)
            print(analyzer.get_info())
            print("-" * 45)
            print("1. Task A (Mass Filtering)")
            print("2. Task B (Orbital Period Stats)")
            print("3. Exit")

            user_choice = validate_input("Select an option: ")

            if user_choice == '1':
                analyzer.perform_task_a()
            elif user_choice == '2':
                analyzer.perform_task_b()
            else:
                print("Analysis completed. Goodbye!")
                break
    except Exception as e:
        print(f"Critical error: {e}")


if __name__ == "__main__":
    main()
# Lab Work: No. 4, Task 3, Variant 26
# Version: 2.0 (Final Comprehensive Version)
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-05-06

import math
import re
import statistics
import os
import matplotlib.pyplot as plt


# --- MIXINS ---

class ValidatorMixin:
    """Mixin for data validation using Regular Expressions."""

    @staticmethod
    def is_valid_number(value_str):
        """Checks if a string is a valid numeric format via Regex."""
        pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)$'
        return bool(re.match(pattern, value_str))


class LoggerMixin:
    """Mixin for logging operations to the console."""

    def log_info(self, message):
        print(f"[INFO]: {message}")


# --- CLASSES ---

class BaseCalculator:
    """Base class for demonstration of inheritance."""

    def __init__(self):
        self._title = "Base Math Module"

    def get_info(self):
        return f"Module: {self._title}"


class LogSeriesCalculator(BaseCalculator, ValidatorMixin, LoggerMixin):
    """
    Main calculator for ln((x+1)/(x-1)) expansion.
    Implements Task 3 requirements: Statistics, Plotting, and File Output.
    """

    def __init__(self, x=2.0, eps=0.0001):
        super().__init__()
        self.__x = x
        self.__eps = eps
        self._title = "Series Analyzer (Variant 26)"

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if value <= 1:
            raise ValueError("Convergence Error: |x| must be > 1.")
        self.__x = value

    @property
    def eps(self):
        return self.__eps

    @eps.setter
    def eps(self, value):
        if value <= 0:
            raise ValueError("Precision must be positive.")
        self.__eps = value

    def calculate_at(self, val_x):
        """Calculates series sum for a specific point x."""
        n = 0
        term = 2 / val_x
        sum_val = term
        while abs(term) > self.__eps and n < 500:
            n += 1
            # Formula: 2 / ((2*n + 1) * x^(2*n + 1))
            term = 2 / ((2 * n + 1) * (val_x ** (2 * n + 1)))
            sum_val += term
        return sum_val, n

    def perform_statistical_analysis(self, data):
        """Calculates required statistical parameters (Task Part 'a')."""
        stats = {
            "Mean": statistics.mean(data),
            "Median": statistics.median(data),
            "Mode": statistics.mode(data),
            "Variance": statistics.variance(data),
            "Std Dev": statistics.stdev(data)
        }
        self.log_info("Statistical parameters for the sequence calculated.")
        return stats

    def create_visual_report(self):
        """Generates plots, table, and saves to file (Task Parts 'b' & 'v')."""
        x_points, y_series, y_math, n_iters = [], [], [], []

        # 1. Data generation
        for i in range(10):
            curr_x = self.__x + (i * 0.4)
            s_val, n = self.calculate_at(curr_x)
            m_val = math.log((curr_x + 1) / (curr_x - 1))

            x_points.append(round(curr_x, 2))
            y_series.append(s_val)
            y_math.append(m_val)
            n_iters.append(n)

        # 2. Print statistics (Part 'a')
        stats = self.perform_statistical_analysis(y_series)
        print("\n--- SEQUENCE STATISTICS (F(x) values) ---")
        for key, val in stats.items():
            print(f"{key}: {val:.6f}")

        # 3. Plotting (Part 'b')
        fig, ax = plt.subplots(figsize=(10, 8))

        # Reference plot (Red Solid)
        ax.plot(x_points, y_math, color='red', label="Math.log (Reference)", linewidth=2)

        # Series plot (Blue Dashed with Markers) - AS REQUESTED: dashed ('--')
        ax.plot(x_points, y_series, 'bo--', label="Series expansion", markersize=6, alpha=0.6)

        # Annotations and Text (Requirement)
        ax.annotate('Best convergence', xy=(x_points[-1], y_series[-1]),
                    xytext=(x_points[-1] - 0.5, y_series[-1] + 0.3),
                    arrowprops=dict(facecolor='black', shrink=0.05))

        ax.text(x_points[0], y_series[0] + 0.1, "Starting point", fontsize=10, color='blue', fontweight='bold')

        # Formatting
        ax.set_title(f"Convergence Analysis: Series vs Math (eps={self.__eps})", fontsize=14)
        ax.set_xlabel("Argument Value (x)", fontsize=12)
        ax.set_ylabel("Function Value F(x)", fontsize=12)
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.legend(loc='upper right')

        # Table inclusion
        table_data = [[x_points[i], n_iters[i], f"{y_series[i]:.5f}", f"{y_math[i]:.5f}"] for i in range(len(x_points))]
        table = plt.table(cellText=table_data, colLabels=["X", "Iter", "Series", "Math"],
                          loc='bottom', bbox=[0, -0.4, 1, 0.25])
        plt.subplots_adjust(bottom=0.3)

        # 4. Saving to file (Part 'v')
        filename = "series_analysis_v26.png"
        plt.savefig(filename, dpi=300)
        self.log_info(f"Plot and report saved to {filename}")

        plt.show()


# --- INTERFACE ---

def get_input(prompt, min_v=None):
    while True:
        s = input(prompt).strip()
        if LogSeriesCalculator.is_valid_number(s):
            v = float(s)
            if min_v is not None and v <= min_v:
                print(f"Error: Value must be > {min_v}")
                continue
            return v
        print("Invalid input. Use numbers only.")


def main():
    print("=== VARIANT 26: LN((X+1)/(X-1)) CALCULATOR ===")
    try:
        x_start = get_input("Enter starting X (X > 1): ", 1)
        eps_val = get_input("Enter precision (e.g. 0.0001): ", 0)

        calc = LogSeriesCalculator(x_start, eps_val)
        calc.create_visual_report()
    except Exception as e:
        print(f"Critical error: {e}")


if __name__ == "__main__":
    main()
# Program: Geometric Shapes Visualization
# Lab Work: No. 4, Task 4, Variant 26 (Rhombus)
# Version: 1.1
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-21

import abc
import math
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from abc import ABC, abstractmethod


# --- DATA CLASSES ---

class Shape(ABC):
    """Abstract base class representing a geometric shape."""

    def __init__(self):
        """Initializes the base shape object."""
        pass

    @abstractmethod
    def calculate_area(self) -> float:
        """Abstract method to calculate the area of the shape."""
        pass


class Color:
    """Class for storing and managing the color of a shape."""

    def __init__(self, color_name: str):
        """Initializes the color with a default value of 'blue'."""
        self.__color = "blue"  # Default fallback color
        self.set_color(color_name)

    def set_color(self, name):
        """
        Validates and sets the color name.
        Uses Regex to ensure the name contains only Latin letters.
        """
        if re.match(r'^[a-zA-Z]+$', name) and name.lower() in mcolors.CSS4_COLORS:
            self.__color = name.lower()
        else:
            print(f"Warning: Color '{name}' not recognized. Defaulting to blue.")
            self.__color = "blue"

    @property
    def value(self):
        """Property to retrieve the validated color string."""
        return self.__color


class Rhombus(Shape):
    """Rhombus class inherited from Shape (Variant 26)."""
    __figure_name = "Rhombus"

    def __init__(self, side: float, angle_deg: float, color_name: str):
        """Initializes Rhombus with side length, angle in degrees, and color."""
        super().__init__()
        self.__side = side
        self.__angle = angle_deg
        self.__color_obj = Color(color_name)

    @classmethod
    def get_name(cls):
        """Returns the localized name of the figure."""
        return cls.__figure_name

    def calculate_area(self) -> float:
        """Calculates the area of the rhombus: S = a^2 * sin(alpha)."""
        rad = math.radians(self.__angle)
        return self.__side ** 2 * math.sin(rad)

    def get_full_info(self) -> str:
        """Returns the shape parameters as a formatted string."""
        info = "Figure: {0}, Side: {1}, Angle: {2}°, Color: {3}, Area: {4:.2f}"
        return info.format(
            self.get_name(),
            self.__side,
            self.__angle,
            self.__color_obj.value,
            self.calculate_area()
        )

    @property
    def side(self): return self.__side

    @property
    def angle(self): return self.__angle

    @property
    def color(self): return self.__color_obj.value


# --- MAIN UTILITIES ---

def validate_input(prompt, min_val, max_val):
    """Validates user numerical input within a specified range."""
    while True:
        try:
            val = float(input(prompt))
            if min_val <= val <= max_val:
                return val
            print(f"Error: Value must be between {min_val} and {max_val}")
        except ValueError:
            print("Error: Please enter a valid number.")


def get_user_data():
    """Handles user input to define shape parameters."""
    print(f"--- Data input for figure: {Rhombus.get_name()} ---")
    side = validate_input("Enter rhombus side length (1-100): ", 1, 100)
    angle = validate_input("Enter acute angle in degrees (1-89): ", 1, 89)
    color = input("Enter figure color (English name, e.g., 'red', 'green'): ").strip()
    label = input("Enter text label for the figure: ")

    rhomb = Rhombus(side, angle, color)
    return rhomb, label


def draw_shape(rhomb: Rhombus, label: str):
    """
    Constructs, colors, and labels the shape using Matplotlib.
    Saves the result to a PNG file.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Calculate rhombus vertex coordinates
    a = rhomb.side
    alpha = math.radians(rhomb.angle)

    # Vertices: (0,0), (a, 0), (a + a*cos(alpha), a*sin(alpha)), (a*cos(alpha), a*sin(alpha))
    vertices = [
        [0, 0],
        [a, 0],
        [a + a * math.cos(alpha), a * math.sin(alpha)],
        [a * math.cos(alpha), a * math.sin(alpha)]
    ]

    # Create the polygon patch
    polygon = patches.Polygon(vertices, closed=True,
                              linewidth=2, edgecolor='black',
                              facecolor=rhomb.color)

    ax.add_patch(polygon)

    # Add text label at the geometric center
    center_x = (a + a * math.cos(alpha)) / 2
    center_y = (a * math.sin(alpha)) / 2
    ax.text(center_x, center_y, label, fontsize=12, ha='center',
            bbox=dict(facecolor='white', alpha=0.7))

    # Configure axes and labels
    limit = a * 2
    ax.set_xlim(-0.5, limit)
    ax.set_ylim(-0.5, limit)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_title(rhomb.get_full_info())

    # Save and display
    plt.savefig("rhombus_output.png")
    print(f"\n[INFO] Figure saved to file 'rhombus_output.png'")
    plt.show()


def main():
    """Main execution entry point."""
    try:
        # Collect data and instantiate object
        rhomb_obj, text_label = get_user_data()

        # Display info in terminal
        print("\n" + "=" * 30)
        print(rhomb_obj.get_full_info())
        print("=" * 30)

        # Draw the shape
        draw_shape(rhomb_obj, text_label)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
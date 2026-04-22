# Program: NumPy Matrix Filtering and Dual Median Calculation
# Lab Work: No. 4, Task 5, Variant 26
# Version: 1.3
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-22

import numpy as np
import re


# --- MODULE 1: MIXINS (Примеси) ---

class StatsValidatorMixin:
    """Mixin to validate data before statistical calculations."""

    def is_not_empty(self, data):
        return data is not None and len(data) > 0


# --- MODULE 2: BASE CLASSES (ООП и наследование) ---

class BaseProcessor:
    """Base class for data processing."""

    def __init__(self):
        self._description = "Базовый процессор данных NumPy"

    def get_info(self):
        """Method for polymorphism."""
        return f"Описание: {self._description}"


class MatrixManager(BaseProcessor, StatsValidatorMixin):
    """
    Class for matrix generation and filtering (Variant 26).
    Demonstrates: static attributes, magic methods, properties, super().
    """
    # Static attribute (Requirement 4)
    total_calculations = 0

    def __init__(self, n, m):
        super().__init__()
        self.__n = n  # Encapsulation
        self.__m = m
        # Create matrix A with random integers (Requirement a.1, a.2)
        self.__matrix_a = np.random.randint(-100, 100, size=(n, m))
        self._description = "Анализатор массива C (Вариант 26)"
        MatrixManager.total_calculations += 1

    # Magic method
    def __str__(self):
        return f"Матрица {self.__n}x{self.__m}, Проверка №{self.total_calculations}"

    # Property (Requirement 4)
    @property
    def source_matrix(self):
        return self.__matrix_a

    # --- Core Logic for Variant 26 ---

    def filter_elements(self, b_value):
        """
        Finds elements where |x| > B and stores them in array C.
        (Requirement 26 part 1)
        """
        # Universal function usage (abs) and indexing/masking (a.3, a.4)
        mask = np.abs(self.__matrix_a) > b_value
        array_c = self.__matrix_a[mask]
        return array_c

    def calculate_medians(self, array_c):
        """
        Calculates median in two ways: via NumPy and manually.
        (Requirement 26 part 2)
        """
        if not self.is_not_empty(array_c):
            print("Массив C пуст. Невозможно вычислить медиану.")
            return

        # Способ 1: Стандартная функция NumPy (Requirement b.2)
        numpy_median = np.median(array_c)

        # Способ 2: Программирование формулы (Manual calculation)
        sorted_c = np.sort(array_c)
        n = len(sorted_c)
        mid = n // 2
        if n % 2 == 0:
            manual_median = (sorted_c[mid - 1] + sorted_c[mid]) / 2
        else:
            manual_median = sorted_c[mid]

        print(f"1. Медиана (NumPy): {numpy_median}")
        print(f"2. Медиана (Ручной расчет): {manual_median}")

        # Additional stats (b.1, b.3, b.4, b.5)
        print(f"Дисперсия массива C: {np.var(array_c):.2f}")
        print(f"Станд. отклонение C: {np.std(array_c):.2f}")


# --- MODULE 3: UTILS (Валидация) ---

def safe_input(prompt, use_regex=True):
    """
    Requirement 8: Protection from incorrect user data.
    Uses Regular Expressions to validate numbers.
    """
    while True:
        raw = input(prompt).strip()
        # Regex for integers (including negative)
        if re.match(r'^-?\d+$', raw):
            return int(raw)
        print("Ошибка! Введите целое число.")


# --- MODULE 4: MAIN (Тестирование) ---

def run_iteration():
    """Single execution of the task."""
    print("\n--- Задание 5: Вариант 26 ---")
    n = safe_input("Введите кол-во строк (n): ")
    m = safe_input("Введите кол-во столбцов (m): ")

    manager = MatrixManager(n, m)
    print(f"\n{manager}")
    print(f"Полиморфизм: {manager.get_info()}")
    print("Матрица A:\n", manager.source_matrix)

    b = safe_input("\nВведите число B для фильтрации (|x| > B): ")

    array_c = manager.filter_elements(b)
    print(f"\nМассив C (элементы > {b} по модулю):", array_c)
    print(f"Количество таких элементов: {len(array_c)}")

    manager.calculate_medians(array_c)


def main():
    """Main loop with repetition logic."""
    while True:
        try:
            run_iteration()
            if input("\nХотите продолжить? (y/n): ").lower() != 'y':
                break
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
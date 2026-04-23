# Program: Exoplanet Data Analysis using real OEC Dataset
# Lab Work: No. 4, Task 6, Variant 26
# Version: 1.2
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-22

import pandas as pd
import re
import os


# --- MODULE 1: MIXINS ---

class DataReportMixin:
    """Mixin to provide formatted reporting for data analysis."""

    def report_step(self, message):
        print(f"\n[STEP]: {message}")
        print("-" * 30)


# --- MODULE 2: BASE CLASSES ---

class BaseDatasetHandler:
    """Base class for handling datasets."""

    def __init__(self, file_path):
        self.file_path = file_path
        self._exists = os.path.exists(file_path)

    def get_info(self):
        """Polymorphic method."""
        return f"File path: {self.file_path} | Status: {'Found' if self._exists else 'Not Found'}"


class PlanetaryAnalyzer(BaseDatasetHandler, DataReportMixin):
    """
    Analyzes exoplanet data using Pandas.
    Demonstrates: static attributes, encapsulation, properties, magic methods.
    """
    # Static attribute (Requirement 4)
    analysis_instances = 0

    def __init__(self, file_path="oec.csv"):
        super().__init__(file_path)
        if not self._exists:
            raise FileNotFoundError(f"Файл {file_path} не найден в папке с программой!")

        # Инкапсуляция: загружаем данные (Requirement 4)
        self.__df = pd.read_csv(file_path)
        PlanetaryAnalyzer.analysis_instances += 1

    # Magic Method (Requirement 4)
    def __str__(self):
        return f"PlanetaryAnalyzer (Rows: {len(self.__df)})"

    # Property (Requirement 4)
    @property
    def data(self):
        return self.__df

    # --- TASK A: Series and Filtering ---
    def perform_task_a(self):
        """
        Creates mass_series, filters mass > 1 (Jupiter mass), and reindexes.
        """
        self.report_step("ЗАДАНИЕ А: Фильтрация Series (Mass > 1)")

        # Создаем Series (используем ID планеты как индекс)
        # В датасете масса указана в массах Юпитера (PlanetaryMassJpt)
        mass_series = self.__df.set_index('PlanetIdentifier')['PlanetaryMassJpt']

        # Удаляем пустые значения перед фильтрацией
        mass_series = mass_series.dropna()

        # Фильтрация (масса > 1 масс Юпитера)
        filtered = mass_series[mass_series > 1]

        # Переиндексация результата
        reindexed_result = filtered.reset_index()

        print(f"Найдено планет с массой > 1 Jpt: {len(reindexed_result)}")
        print(reindexed_result.head(10))  # Вывод первых 10 для краткости

    # --- TASK B: Statistical Analysis ---
    def perform_task_b(self):
        """
        Calculates ratio of avg periods for max vs min radius planets.
        """
        self.report_step("ЗАДАНИЕ Б: Статистика (Period vs Radius)")

        df = self.__df[['PlanetIdentifier', 'RadiusJpt', 'PeriodDays']].dropna()

        if df.empty:
            print("Недостаточно данных для расчета (пустые значения).")
            return

        # Находим макс и мин радиус
        max_r = df['RadiusJpt'].max()
        min_r = df['RadiusJpt'].min()

        # Средний период обращения (PeriodDays) для таких планет
        avg_period_max = df[df['RadiusJpt'] == max_r]['PeriodDays'].mean()
        avg_period_min = df[df['RadiusJpt'] == min_r]['PeriodDays'].mean()

        # Расчет отношения
        ratio = avg_period_max / avg_period_min

        print(f"Макс. радиус: {max_r} Jpt, Средний период: {avg_period_max:.2f} дн.")
        print(f"Мин. радиус: {min_r} Jpt, Средний период: {avg_period_min:.2f} дн.")
        print(f"\nРЕЗУЛЬТАТ: Период макс. планет в {ratio:.2f} раз больше мин. планет.")


# --- MODULE 3: INTERFACE ---

def validate_input(prompt):
    """Protection using Regex (Requirement 8)."""
    while True:
        choice = input(prompt).strip()
        if re.match(r'^[1-3]$', choice):
            return choice
        print("Ошибка! Введите число от 1 до 3.")


def main():
    """Main testing module (Requirement 7)."""
    try:
        analyzer = PlanetaryAnalyzer("oec.csv")

        while True:
            print("\n" + "=" * 45)
            print("АНАЛИЗ ЭКЗОПЛАНЕТ (CSV) - ВАРИАНТ 26")
            print("=" * 45)
            print(f"Инфо: {analyzer.get_info()}")
            print("-" * 45)
            print("1. Задание А (Фильтрация масс)")
            print("2. Задание Б (Статистика периодов)")
            print("3. Выход")

            choice = validate_input("Выберите пункт меню: ")

            if choice == '1':
                analyzer.perform_task_a()
            elif choice == '2':
                analyzer.perform_task_b()
            else:
                print("Программа завершена.")
                break
    except Exception as e:
        print(f"Ошибка при работе с файлом: {e}")


if __name__ == "__main__":
    main()
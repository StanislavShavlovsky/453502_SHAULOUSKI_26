# Lab Work: No. 4, Task 3, Variant 26
# Version: 1.3
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-21

import math
import re
import matplotlib.pyplot as plt


# --- ПРИМЕСИ (MIXINS) ---

class ValidatorMixin:
    """Примесь для валидации данных с использованием регулярных выражений."""

    @staticmethod
    def is_valid_number(value_str):
        """Проверяет, является ли строка корректным числом через Regex."""
        # Паттерн: возможный знак, цифры, возможная точка и еще цифры
        pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)$'
        return bool(re.match(pattern, value_str))


class LoggerMixin:
    """Примесь для логирования операций в консоль."""

    def log_info(self, message):
        print(f"[ИНФО]: {message}")


# --- КЛАССЫ ---

class BaseCalculator:
    """Базовый класс для демонстрации наследования и полиморфизма."""

    def __init__(self):
        self._title = "Базовый математический модуль"

    def get_info(self):
        """Пример метода для полиморфного переопределения."""
        return f"Тип объекта: {self._title}"


class LogSeriesCalculator(BaseCalculator, ValidatorMixin, LoggerMixin):
    """
    Класс для расчета ряда ln((x+1)/(x-1)).
    Реализует: статические атрибуты, инкапсуляцию, свойства, магические методы.
    """
    # Статический атрибут класса
    total_objects_created = 0

    def __init__(self, x=2.0, eps=0.0001):
        # Использование super() для инициализации предка
        super().__init__()
        self.__x = x  # Приватный атрибут (инкапсуляция)
        self.__eps = eps  # Приватный атрибут
        self._title = "Анализатор ряда ln((x+1)/(x-1))"
        LogSeriesCalculator.total_objects_created += 1

    # Геттеры и сеттеры (Свойства / Properties)
    @property
    def x(self):
        """Возвращает значение X."""
        return self.__x

    @x.setter
    def x(self, value):
        """Устанавливает X с проверкой условия области сходимости."""
        if value <= 1:
            raise ValueError("Ошибка: Для сходимости ряда |x| должен быть > 1.")
        self.__x = value

    @property
    def eps(self):
        """Возвращает точность EPS."""
        return self.__eps

    @eps.setter
    def eps(self, value):
        """Устанавливает точность с проверкой на положительность."""
        if value <= 0:
            raise ValueError("Ошибка: Точность должна быть больше 0.")
        self.__eps = value

    # Магические (специальные) методы
    def __str__(self):
        """Строковое представление объекта для пользователя."""
        return f"Калькулятор (x={self.__x}, eps={self.__eps})"

    def __repr__(self):
        """Официальное представление объекта для разработчика."""
        return f"LogSeriesCalculator(x={self.__x}, eps={self.__eps})"

    # Полиморфизм (переопределение метода базового класса)
    def get_info(self):
        base_msg = super().get_info()
        return f"{base_msg} | Вариант 26 (Степенные ряды)"

    # Бизнес-логика (расчет ряда)
    def calculate_at(self, custom_x=None):
        """Вычисляет значение ряда в точке X с заданной точностью."""
        val_x = custom_x if custom_x is not None else self.__x
        n = 0
        # Первый член ряда при n=0
        term = 2 / val_x
        sum_val = term

        while abs(term) > self.__eps and n < 1000:
            n += 1
            # Формула члена ряда: 2 / ((2n + 1) * x^(2n + 1))
            term = 2 / ((2 * n + 1) * (val_x ** (2 * n + 1)))
            sum_val += term
        return sum_val, n

    def create_visual_report(self):
        """Создает график, таблицу и СОХРАНЯЕТ результат в файл."""
        x_points = []
        y_series = []
        y_math = []
        n_iters = []

        self.log_info("Выполняю расчеты для 8 контрольных точек...")

        # Генерируем данные для графика (шаг 0.5 от текущего X)
        for i in range(8):
            curr_x = self.__x + (i * 0.5)
            s_val, n = self.calculate_at(curr_x)
            m_val = math.log((curr_x + 1) / (curr_x - 1))

            x_points.append(round(curr_x, 2))
            y_series.append(s_val)
            y_math.append(m_val)
            n_iters.append(n)

        # Построение графика
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.plot(x_points, y_math, 'r-', label="Эталон (math.log)", linewidth=2)
        ax.plot(x_points, y_series, 'bo--', label="Сумма ряда", markersize=5, alpha=0.6)

        ax.set_title(f"Анализ сходимости ряда (Вариант 26, eps={self.__eps})")
        ax.set_xlabel("Значение аргумента X")
        ax.set_ylabel("Значение функции Y")
        ax.legend()
        ax.grid(True, linestyle=':')

        # Создание таблицы под графиком
        table_columns = ["X", "Итерации", "Ряд", "Math Log", "Точность"]
        table_data = []
        for i in range(len(x_points)):
            table_data.append([
                f"{x_points[i]}", f"{n_iters[i]}",
                f"{y_series[i]:.6f}", f"{y_math[i]:.6f}", f"{self.__eps}"
            ])

        plt.table(cellText=table_data, colLabels=table_columns, loc='bottom', bbox=[0, -0.45, 1, 0.3])
        plt.subplots_adjust(left=0.1, bottom=0.35)

        # СОХРАНЕНИЕ В ФАЙЛ (Пункт "в" задания)
        output_image = "output_plot_v26.png"
        plt.savefig(output_image, dpi=300)
        self.log_info(f"График успешно сохранен в файл: {output_image}")

        print("Отображение графика... (закройте окно, чтобы продолжить)")
        plt.show()


# --- ФУНКЦИИ ИНТЕРФЕЙСА ---

def get_user_input(prompt, min_val=None):
    """Обеспечивает защиту от некорректного ввода с использованием Regex."""
    while True:
        val_str = input(prompt).strip()
        if LogSeriesCalculator.is_valid_number(val_str):
            val = float(val_str)
            if min_val is not None and val <= min_val:
                print(f"Ошибка: Значение должно быть больше {min_val}.")
                continue
            return val
        print("Некорректный ввод! Используйте только цифры и точку.")


def main():
    """Главная функция программы."""
    print("=" * 60)
    print("  ПРОГРАММА ВИЗУАЛИЗАЦИИ МАТЕМАТИЧЕСКОГО РЯДА (ВАРИАНТ 26)")
    print("=" * 60)

    while True:
        try:
            # Ввод данных
            x_val = get_user_input("Введите стартовое значение X (X > 1): ", 1)
            e_val = get_user_input("Введите точность вычислений (например, 0.0001): ", 0)

            # Создание объекта и работа с ООП
            calc = LogSeriesCalculator(x_val, e_val)

            print(f"\n{calc.get_info()}")
            print(f"Объект: {calc}")

            # Генерация отчета и графика
            calc.create_visual_report()

            # Возможность повтора
            ans = input("\nВыполнить еще один расчет? (д/н): ").lower()
            if ans not in ['д', 'y', 'yes', 'l']:
                print(f"\nЗавершение работы. Создано объектов за сессию: {calc.total_objects_created}")
                break

        except Exception as e:
            print(f"Произошла ошибка в основном цикле: {e}")


if __name__ == "__main__":
    main()
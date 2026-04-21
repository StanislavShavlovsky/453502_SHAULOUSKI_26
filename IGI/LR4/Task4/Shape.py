# Program: Geometric Shapes Visualization
# Lab Work: No. 4, Task 4, Variant 26 (Rhombus)
# Version: 1.0
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-21

import abc
import math
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from abc import ABC, abstractmethod


# --- КЛАССЫ ДАННЫХ ---

class Shape(ABC):
    """Абстрактный класс геометрической фигуры."""

    def __init__(self):
        # Сообщение инициализации, как в примере
        pass

    @abstractmethod
    def calculate_area(self) -> float:
        """Абстрактный метод для вычисления площади."""
        pass


class Color:
    """Класс для хранения и управления цветом фигуры."""

    def __init__(self, color_name: str):
        self.__color = "blue"  # Цвет по умолчанию
        self.set_color(color_name)

    def set_color(self, name):
        # Валидация: название цвета должно состоять только из латинских букв (Regex)
        if re.match(r'^[a-zA-Z]+$', name) and name.lower() in mcolors.CSS4_COLORS:
            self.__color = name.lower()
        else:
            print(f"Предупреждение: Цвет '{name}' не распознан. Установлен синий.")
            self.__color = "blue"

    @property
    def value(self):
        """Свойство для получения значения цвета."""
        return self.__color


class Rhombus(Shape):
    """Класс Ромб, наследуемый от Геометрической фигуры."""
    __figure_name = "Ромб"

    def __init__(self, side: float, angle_deg: float, color_name: str):
        super().__init__()
        self.__side = side
        self.__angle = angle_deg
        self.__color_obj = Color(color_name)

    @classmethod
    def get_name(cls):
        """Возвращает название фигуры."""
        return cls.__figure_name

    def calculate_area(self) -> float:
        """Вычисляет площадь ромба: S = a^2 * sin(R)."""
        rad = math.radians(self.__angle)
        return self.__side ** 2 * math.sin(rad)

    def get_full_info(self) -> str:
        """Возвращает параметры фигуры в виде отформатированной строки."""
        info = "Фигура: {0}, Сторона: {1}, Угол: {2}°, Цвет: {3}, Площадь: {4:.2f}"
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


# --- ОСНОВНЫЕ ФУНКЦИИ ---

def validate_input(prompt, min_val, max_val):
    """Проверка корректности ввода числовых данных."""
    while True:
        try:
            val = float(input(prompt))
            if min_val <= val <= max_val:
                return val
            print(f"Ошибка: значение должно быть в диапазоне от {min_val} до {max_val}")
        except ValueError:
            print("Ошибка: введите корректное число.")


def get_user_data():
    """1. Ввод значений пользователем."""
    print(f"--- Ввод данных для фигуры: {Rhombus.get_name()} ---")
    side = validate_input("Введите длину стороны ромба (1-100): ", 1, 100)
    angle = validate_input("Введите острый угол в градусах (1-89): ", 1, 89)
    color = input("Введите цвет фигуры (на английском, например, 'red', 'green'): ").strip()
    label = input("Введите текст подписи для фигуры: ")

    rhomb = Rhombus(side, angle, color)
    return rhomb, label


def draw_shape(rhomb: Rhombus, label: str):
    """3. Построение, закрашивание и подпись фигуры."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # Координаты ромба
    a = rhomb.side
    alpha = math.radians(rhomb.angle)

    # Вершины ромба: (0,0), (a, 0), (a + a*cos(alpha), a*sin(alpha)), (a*cos(alpha), a*sin(alpha))
    vertices = [
        [0, 0],
        [a, 0],
        [a + a * math.cos(alpha), a * math.sin(alpha)],
        [a * math.cos(alpha), a * math.sin(alpha)]
    ]

    # Создание полигона
    polygon = patches.Polygon(vertices, closed=True,
                              linewidth=2, edgecolor='black',
                              facecolor=rhomb.color)

    ax.add_patch(polygon)

    # Добавление подписи (текста)
    center_x = (a + a * math.cos(alpha)) / 2
    center_y = (a * math.sin(alpha)) / 2
    ax.text(center_x, center_y, label, fontsize=12, ha='center',
            bbox=dict(facecolor='white', alpha=0.7))

    # Настройка осей
    limit = a * 2
    ax.set_xlim(-0.5, limit)
    ax.set_ylim(-0.5, limit)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_title(rhomb.get_full_info())

    # 4. Вывод на экран и сохранение в файл
    plt.savefig("rhombus_output.png")
    print(f"\n[ИНФО] Фигура сохранена в файл 'rhombus_output.png'")
    plt.show()


def main():
    """Тестирование классов."""
    try:
        # Получаем данные и создаем объект
        rhomb_obj, text_label = get_user_data()

        # Вывод информации в консоль
        print("\n" + "=" * 30)
        print(rhomb_obj.get_full_info())
        print("=" * 30)

        # Отрисовка
        draw_shape(rhomb_obj, text_label)

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
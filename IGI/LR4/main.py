# Program: Main Integration Module for Laboratory Work No. 4
# Lab Work: No. 4 (Tasks 1-6)
# Version: 1.0
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-23

import re
import sys


def validate_menu_input(prompt):
    """
    Валидация выбора меню с использованием регулярных выражений.
    Соответствует требованию №8 (защита от некорректных данных).
    """
    while True:
        user_input = input(prompt).strip()
        # регулярка - цифры от 0 до 6
        if re.match(r'^[0-6]$', user_input):
            return int(user_input)
        print("Ошибка! Введите число от 1 до 6 (или 0 для выхода).")


def main():
    """
    Центральный модуль управления лабораторной работой.
    Интерфейс сделан максимально простым и понятным.
    """

    print("ЛАБОРАТОРНАЯ РАБОТА №4. ВАРИАНТ 26")

    while True:
        print("\nСПИСОК ЗАДАНИЙ:")
        print("1. Сериализация (Деревья)")
        print("2. Анализ текста (Регулярные выражения)")
        print("3. Вычисление ряда (Логарифм)")
        print("4. Геометрия (Ромб)")
        print("5. Матрицы (NumPy)")
        print("6. Анализ планет (Pandas)")
        print("0. Выход")

        choice = validate_menu_input("\nВыберите номер задания (0-6): ")

        if choice == 0:
            print("\nПрограмма завершена. До свидания!")
            break

        try:
            # вызов модулей в зависимости от выбора
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
            print(f"\nОшибка: Не удалось найти файл модуля. Проверьте название: {e}")
        except AttributeError:
            print(f"\nОшибка: В модуле {choice} не найдена функция main().")
        except Exception as e:
            print(f"\nПроизошла ошибка при выполнении задания {choice}: {e}")

        input("\nНажмите Enter, чтобы вернуться в меню...")


if __name__ == "__main__":
    main()
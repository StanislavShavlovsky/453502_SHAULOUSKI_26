import Task_1
import Task_2
import Task_3
import Task_4
import Task_5

def run_menu():
    """
    Главное меню для выбора лабораторных работ.
    """
    while True:
        print("   ВЫБОР ЗАДАНИЯ (Лабораторная №3)")
        print("1. Расчет бесконечного ряда ln((x+1)/(x-1))")
        print("2. Среднее арифметическое четных чисел")
        print("3. Подсчет слов с маленькой буквы")
        print("4. Анализ текста (Алиса в стране чудес)")
        print("5. Обработка списка вещественных чисел")
        print("0. Выход")

        choice = input("Выберите номер задачи (0-5): ").strip()

        if choice == '1':
            # В Task_1.py основная логика обернута декоратором @repeatable
            Task_1.main()
        elif choice == '2':
            Task_2.main()
        elif choice == '3':
            Task_3.main()
        elif choice == '4':
            Task_4.main()
        elif choice == '5':
            Task_5.main()
        elif choice == '0':
            print("Завершение работы. До свидания!")
            break
        else:
            print("Ошибка: введите число от 0 до 5.")

if __name__ == "__main__":
    try:
        run_menu()
    except KeyboardInterrupt:
        print("\nПрограмма принудительно остановлена.")
import Task_1
import Task_2
import Task_3
import Task_4
import Task_5

def run_menu():
    """
    Main menu for laboratory work selection.
    """
    while True:
        print("MENU FOR LAB WORK 3 VARIANT 26")
        print("1. Power series calculation: ln((x+1)/(x-1))")
        print("2. Arithmetic mean of even numbers")
        print("3. Count words starting with lowercase")
        print("4. Text Analysis (Alice in Wonderland)")
        print("5. Real numbers list processing")
        print("0. Exit")

        choice = input("Select a task number (0-5): ").strip()

        if choice == '1':
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
            print("Exiting program. Goodbye!")
            break
        elif choice == '999':  # secret code for testing error
            raise RuntimeError("Тестовый сбой системы!")
        else:
            print("Error: Please enter a number between 0 and 5.")

if __name__ == "__main__":
    try:
        run_menu()
    except KeyboardInterrupt:
        print("\nProgram forcibly stopped by user.")
    except Exception as e:
        # Notice user
        print(f"\n[CRITICAL ERROR]: {e}")
        raise
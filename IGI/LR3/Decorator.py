def repeatable(func):
    """
    A decorator that allows you to repeat a
    function's execution without restarting the script.
    """
    def wrapper(*args, **kwargs):
        while True:
            func(*args, **kwargs)
            again = input("\nLaunch again? (y/n): ").strip().lower()
            if again != 'y':
                print("Completion of work.")
                break
    return wrapper
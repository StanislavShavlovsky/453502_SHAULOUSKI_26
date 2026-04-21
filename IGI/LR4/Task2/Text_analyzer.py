# Lab Work: No. 4, Task 2, Variant 26
# Version: 1.7 (Final Compliance)
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-21

import re
import os
from zipfile import ZipFile


class TextAnalyzer:
    def __init__(self):
        self.__source_text = ""

    @property
    def source_text(self):
        return self.__source_text

    @source_text.setter
    def source_text(self, value):
        self.__source_text = value

    def read_file(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден.")
        with open(filename, 'r', encoding='utf-8') as f:
            self.__source_text = f.read()

    # --- ОБЩЕЕ ЗАДАНИЕ ---
    def get_general_stats(self):
        sentences = re.findall(r'[^.!?]+[.!?]', self.__source_text)
        total_s = len(sentences)
        decl = len(re.findall(r'(?<!\?)(?<!\!)\.(?!\.)', self.__source_text))
        ques = len(re.findall(r'\?', self.__source_text))
        imp = len(re.findall(r'\!', self.__source_text))

        words = re.findall(r'\b\w+\b', self.__source_text)
        avg_word = round(sum(len(w) for w in words) / len(words), 2) if words else 0

        # Смайлики по условию: [;:] + [-]* + одинаковые [()\[\]]+
        smiles = len(re.findall(r'[;:][-]*(\(+|\)+|\[+|\]+)', self.__source_text))

        return total_s, decl, ques, imp, avg_word, smiles

    # --- ЗАДАНИЕ ВАРИАНТА 26 ---

    def get_lowercase_consonant_words(self):
        """1. Слова, начинающиеся со строчной согласной буквы."""
        # Согласные: bcdfghjklmnpqrstvwxz + бвгджзйклмнпрстфхцчшщ (строчные)
        pattern = r'\b[bcdfghjklmnpqrstvwxzбвгджзйклмнпрстфхцчшщ]\w*'
        return re.findall(pattern, self.__source_text)

    def find_car_numbers(self):
        """2. Поиск корректных автомобильных номеров (Формат: БЦЦЦББ РР)."""
        # Пример: A123BC 77 или 1234 AB-7
        pattern = r'\b[A-ZА-Я]\d{3}[A-ZА-Я]{2}\s?\d{2,3}\b|\b\d{4}\s?[A-ZА-Я]{2}-\d\b'
        return re.findall(pattern, self.__source_text)

    def count_min_length_words(self):
        """3. Сколько слов имеют минимальную длину."""
        words = re.findall(r'\b\w+\b', self.__source_text)
        if not words: return 0, 0
        min_len = min(len(w) for w in words)
        min_words = [w for w in words if len(w) == min_len]
        return min_len, len(min_words)

    def words_before_comma(self):
        """4. Все слова, за которыми следует запятая."""
        return re.findall(r'\b\w+(?=\,)', self.__source_text)

    def longest_word_ends_y(self):
        """5. Самое длинное слово, которое заканчивается на 'y'."""
        words_y = re.findall(r'\b\w*y\b', self.__source_text, re.IGNORECASE)
        if not words_y: return None
        return max(words_y, key=len)


def solve_task_2():
    analyzer = TextAnalyzer()
    input_file = "input_task2.txt"

    # Создание тестового файла, если его нет
    if not os.path.exists(input_file):
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("apple, sky, fly. Студент ехал на A123BC 77. Тут есть ;---))) и :[[[. "
                    "город, машина, яма. Самое длинное слово - dictionary.")

    try:
        analyzer.read_file(input_file)
    except Exception as e:
        print(e)
        return

    # Сбор данных
    total, d, q, i, avg_w, smiles = analyzer.get_general_stats()
    low_cons = analyzer.get_lowercase_consonant_words()
    cars = analyzer.find_car_numbers()
    min_l, min_c = analyzer.count_min_length_words()
    bef_comma = analyzer.words_before_comma()
    long_y = analyzer.longest_word_ends_y()

    # Формирование вывода
    output = []
    output.append(f"--- ОБЩАЯ СТАТИСТИКА ---")
    output.append(f"Предложений: {total} (Повеств: {d}, Вопросительный: {q}, Побудительный: {i})")
    output.append(f"Средняя длина слова: {avg_w}")
    output.append(f"Кол-во смайликов: {smiles}")

    output.append(f"\n--- ВАРИАНТ 26 ---")
    output.append(f"1. Слова на строчную согласную: {low_cons}")
    output.append(f"2. Найденные авто-номера: {cars}")
    output.append(f"3. Слов с мин. длиной ({min_l} симв.): {min_c}")
    output.append(f"4. Слова перед запятой: {bef_comma}")
    output.append(f"5. Самое длинное на 'y': {long_y}")

    final_text = "\n".join(output)
    print(final_text)

    # Сохранение и архивация
    res_file = "result_26.txt"
    with open(res_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    with ZipFile("archive_26.zip", "w") as zf:
        zf.write(res_file, arcname="report.txt")
        print(f"\n[Инфо] Файл заархивирован. Размер: {zf.getinfo('report.txt').file_size} байт.")


if __name__ == "__main__":
    solve_task_2()
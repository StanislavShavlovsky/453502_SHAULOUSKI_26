# Lab Work: No. 4, Task 2, Variant 26
# Version: 1.8 (English Documentation)
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-21

import re
import os
from zipfile import ZipFile


class TextAnalyzer:
    """Class for performing linguistic analysis on text using Regular Expressions."""

    def __init__(self):
        """Initializes the analyzer with an empty source text."""
        self.__source_text = ""

    @property
    def source_text(self):
        """Property to get the current source text."""
        return self.__source_text

    @source_text.setter
    def source_text(self, value):
        """Property to set the source text manually."""
        self.__source_text = value

    def read_file(self, filename):
        """Reads text from a file and stores it in the private attribute."""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} not found.")
        with open(filename, 'r', encoding='utf-8') as f:
            self.__source_text = f.read()

    # --- GENERAL TASKS ---
    def get_general_stats(self):
        """Calculates general text statistics: sentence types, avg word length, and emoticons."""
        # Split sentences by punctuation marks
        sentences = re.findall(r'[^.!?]+[.!?]', self.__source_text)
        total_s = len(sentences)

        # Count types using Look-around assertions
        decl = len(re.findall(r'(?<!\?)(?<!\!)\.(?!\.)', self.__source_text))
        ques = len(re.findall(r'\?', self.__source_text))
        imp = len(re.findall(r'\!', self.__source_text))

        # Word analysis
        words = re.findall(r'\b\w+\b', self.__source_text)
        avg_word = round(sum(len(w) for w in words) / len(words), 2) if words else 0

        # Emoticon detection: [eyes] + [optional nose] + [repeating mouth symbols]
        smiles = len(re.findall(r'[;:][-]*(\(+|\)+|\[+|\]+)', self.__source_text))

        return total_s, decl, ques, imp, avg_word, smiles

    # --- VARIANT 26 SPECIFIC TASKS ---

    def get_lowercase_consonant_words(self):
        """1. Finds all words starting with a lowercase consonant letter."""
        pattern = r'\b[bcdfghjklmnpqrstvwxzбвгджзйклмнпрстфхцчшщ]\w*'
        return re.findall(pattern, self.__source_text)

    def find_car_numbers(self):
        """2. Search for valid car license plates (Formats: LDDDLL or DDDD LL-D)."""
        # Supports Russian/European and Belarusian formats
        pattern = r'\b[A-ZА-Я]\d{3}[A-ZА-Я]{2}\s?\d{2,3}\b|\b\d{4}\s?[A-ZА-Я]{2}-\d\b'
        return re.findall(pattern, self.__source_text)

    def count_min_length_words(self):
        """3. Counts how many words have the minimum length found in the text."""
        words = re.findall(r'\b\w+\b', self.__source_text)
        if not words: return 0, 0
        min_len = min(len(w) for w in words)
        min_words = [w for w in words if len(w) == min_len]
        return min_len, len(min_words)

    def words_before_comma(self):
        """4. Finds all words followed immediately by a comma."""
        return re.findall(r'\b\w+(?=\,)', self.__source_text)

    def longest_word_ends_y(self):
        """5. Finds the longest word that ends with the letter 'y'."""
        words_y = re.findall(r'\b\w*y\b', self.__source_text, re.IGNORECASE)
        if not words_y: return None
        return max(words_y, key=len)


def solve_task_2():
    """Main function to execute Task 2 logic and save results to a ZIP archive."""
    analyzer = TextAnalyzer()
    input_file = "input_task2.txt"

    # Create a test file if it doesn't exist
    if not os.path.exists(input_file):
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("apple, sky, fly. Student drove A123BC 77. Here is ;---))) and :[[[. "
                    "city, car, pit. The longest word is dictionary.")

    try:
        analyzer.read_file(input_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Data collection
    total, d, q, i, avg_w, smiles = analyzer.get_general_stats()
    low_cons = analyzer.get_lowercase_consonant_words()
    cars = analyzer.find_car_numbers()
    min_l, min_c = analyzer.count_min_length_words()
    bef_comma = analyzer.words_before_comma()
    long_y = analyzer.longest_word_ends_y()

    # Formulating the report
    output = []
    output.append("--- GENERAL STATISTICS ---")
    output.append(f"Sentences: {total} (Decl: {d}, Interrogative: {q}, Imperative: {i})")
    output.append(f"Average word length: {avg_w}")
    output.append(f"Emoticons count: {smiles}")

    output.append("\n--- VARIANT 26 RESULTS ---")
    output.append(f"1. Words starting with lowercase consonant: {low_cons}")
    output.append(f"2. Found license plates: {cars}")
    output.append(f"3. Words with min length ({min_l} chars): {min_c}")
    output.append(f"4. Words followed by comma: {bef_comma}")
    output.append(f"5. Longest word ending in 'y': {long_y}")

    final_text = "\n".join(output)
    print(final_text)

    # Save to file and archive
    res_file = "result_26.txt"
    with open(res_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    # Creating ZIP archive
    with ZipFile("archive_26.zip", "w") as zf:
        zf.write(res_file, arcname="report.txt")
        print(f"\n[INFO] Report archived. Size: {zf.getinfo('report.txt').file_size} bytes.")


if __name__ == "__main__":
    solve_task_2()
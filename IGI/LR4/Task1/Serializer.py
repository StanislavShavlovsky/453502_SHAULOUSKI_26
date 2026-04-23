# Lab Work: No. 4, Task 1, Variant 26
# Version: 1.5
# Developer: Shaulouski Stanislau Andreevich
# Date: 2026-04-21

import csv
import pickle
import os

# mixins
class SerializationMixin:
    """Base mixin for file operations help."""
    @staticmethod
    def check_file(filename):
        """Static method example: checks if file exists."""
        return os.path.exists(filename)


class CsvMixin(SerializationMixin):
    def save_to_csv(self, trees, filename):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["species", "total_count", "healthy_count"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in trees:
                writer.writerow({
                    "species": t.species,
                    "total_count": t.total_count,
                    "healthy_count": t.healthy_count
                })


class PickleMixin(SerializationMixin):
    def save_to_pickle(self, trees, filename):
        with open(filename, "wb") as f:
            pickle.dump(trees, f)


# ооp

class BiologicalEntity:  # base class
    """Base class to demonstrate inheritance and super()."""
    def __init__(self, species):
        self._species = species.capitalize()  # Encapsulation

    @property
    def species(self):
        return self._species


class ForestTree(BiologicalEntity):
    """Main class for Variant 26."""
    instance_count = 0  # Static attribute

    def __init__(self, species, total_count, healthy_count):
        super().__init__(species)
        self.total_count = total_count
        self.healthy_count = healthy_count
        ForestTree.instance_count += 1

    @property
    def sick_count(self):
        """Dynamic attribute calculation."""
        return self.total_count - self.healthy_count

    def get_sick_percent(self):
        if self.total_count == 0: return 0
        return round((self.sick_count / self.total_count) * 100, 2)

    def __str__(self):
        return f"Дерево(Вид: {self.species}, Всего: {self.total_count}, Здоровых: {self.healthy_count})"


# main service

class ForestManager(CsvMixin, PickleMixin):
    def __init__(self, csv_fn, pkl_fn):
        self.csv_fn = csv_fn
        self.pkl_fn = pkl_fn
        self.tree_objects = []

    def load_initial_data(self, data_list):
        for item in data_list:
            self.tree_objects.append(
                ForestTree(item["species"], item["total_count"], item["healthy_count"])
            )
        self.tree_objects.sort(key=lambda x: x.species)

    def run(self):
        while True:
            print("\n СИСТЕМА УЧЕТА ЛЕСА (ВАР 26) ")
            print("1. Рассчитать общую статистику и проценты")
            print("2. Поиск вида в CSV файле")
            print("3. Показать все записи (из CSV)")
            print("4. Сохранить текущие данные (CSV/Pickle)")
            print("0. Выход")

            cmd = input("\nВыберите действие: ")

            if cmd == "1":
                total_all = sum(t.total_count for t in self.tree_objects)
                total_healthy = sum(t.healthy_count for t in self.tree_objects)
                if total_all > 0:
                    print(f"\n[ОБЩИЕ ДАННЫЕ] Всего деревьев: {total_all}")
                    print(f"[ОБЩИЕ ДАННЫЕ] Здоровых: {total_healthy}")
                    print(f"[ОБЩИЕ ДАННЫЕ] % больных: {((total_all - total_healthy) / total_all) * 100:.2f}%")
                    print("\n[АНАЛИЗ ПО ВИДАМ]")
                    for t in self.tree_objects:
                        part = (t.total_count / total_all) * 100
                        print(f"- {t.species}: {part:.1f}% от всего леса. Больных в виде: {t.get_sick_percent()}%")
                else:
                    print("\nДанные отсутствуют.")

            elif cmd == "2":
                q = input("Введите название вида для поиска: ").capitalize()
                if self.check_file(self.csv_fn):
                    with open(self.csv_fn, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        found = [row for row in reader if row['species'] == q]
                        if found:
                            for item in found: print(f"Найдено: {item}")
                        else:
                            print("Вид не найден.")
                else:
                    print("Файл CSV еще не создан. Сначала сохраните данные (пункт 4).")

            elif cmd == "3":
                self.save_to_csv(self.tree_objects, self.csv_fn)
                print("\nСодержимое CSV файла:")
                if self.check_file(self.csv_fn):
                    with open(self.csv_fn, "r", encoding="utf-8") as f:
                        print(f.read())

            elif cmd == "4":
                self.save_to_csv(self.tree_objects, self.csv_fn)
                self.save_to_pickle(self.tree_objects, self.pkl_fn)
                print(f"Данные успешно сохранены в {self.csv_fn} и {self.pkl_fn}")

            elif cmd == "0":
                print("Завершение работы.")
                break
            else:
                print("Некорректный ввод, попробуйте снова.")


HARDCODED_DATA = [
    {"species": "Дуб", "total_count": 500, "healthy_count": 420},
    {"species": "Сосна", "total_count": 800, "healthy_count": 600},
    {"species": "Береза", "total_count": 300, "healthy_count": 290}
]

if __name__ == "__main__":
    manager = ForestManager("forest.csv", "forest.pkl")
    manager.load_initial_data(HARDCODED_DATA)
    manager.run()
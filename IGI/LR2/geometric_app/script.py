import json
from geometric_lib.square import area as square_area
from geometric_lib.circle import area as circle_area


with open("config.json", "r", encoding="utf-8") as f:
    data = json.load(f)

side = data.get("side", 5)
radius = data.get("radius", 3)

print(" Геометрические вычисления ")
print(f"Площадь квадрата со стороной {side}: {square_area(side)}")
print(f"Площадь круга радиуса {radius}: {circle_area(radius)}")

#!/usr/bin/env python3
"""
A tool that generates a chart comparing the gears of several bikes.
"""
import argparse
import itertools
import math
from dataclasses import dataclass

import pygame

UNITS = {
    "km": 1000,
    "m": 1,
    "dm": 0.1,
    "cm": 0.01,
    "mm": 0.001,
    "ft": 0.3048,
    "in": 0.0254,
}

BACK_COLOUR = (0, 0, 0)
LINE_COLOUR = (119, 119, 119)
BLOB_COLOUR = (200, 200, 200)
LABEL_COLOUR = (255, 255, 255)


class Length(float):
    def __new__(cls, value, unit="mm"):
        return super().__new__(cls, UNITS[unit] * value)


def get_full_radius(data):
    if "full_radius" not in data:
        result = 0
        if "wheel_radius" in data:
            result += data["wheel_radius"]
        elif "wheel_diameter" in data:
            result += data["wheel_diameter"] / 2

        if "tyre_thickness" in data:
            result += data["tyre_thickness"]

        if "full_diameter" in data:
            result = data["full_diameter"] / 2

        elif "full_circumference" in data:
            result = data["full_circumference"] / math.tau

    for used_key in (
        "wheel_radius",
        "wheel_diameter",
        "tyre_thickness",
        "full_diameter",
        "full_circumference",
    ):
        if used_key in data:
            del data[used_key]
    data["full_radius"] = result
    return data


def gear_ratio(front, rear):
    return front / rear


def development(front, rear, full_radius):
    return front / rear * full_radius * math.tau


def gear_inches(*args):
    return development(*args) / math.pi / UNITS["in"]


def gain_ratio(front, rear, full_radius, crank):
    return front / rear * full_radius / crank


@dataclass
class Bike:
    name: str
    front: list
    rear: list
    full_radius: Length = Length(700, "mm")
    crank: Length = Length(172.5, "mm")

    def get_gain_ratios(self):
        ratios = [
            (
                gain_ratio(f, r, self.full_radius, self.crank),
                (self.index_front(f) + 1, self.index_rear(r) + 1),
            )
            for f, r in itertools.product(self.front, self.rear)
        ]
        ratios.sort()
        return ratios

    def index_front(self, value):
        return sorted(self.front).index(value)

    def index_rear(self, value):
        return sorted(self.rear, reverse=True).index(value)


def load_bikes(file_obj):
    """Generate a list of bikes by parsing a file."""
    bikes = []
    current_data = {}
    for row in file_obj:
        row = row.strip()
        if row[0] == "#":
            if current_data:
                bikes.append(Bike(**get_full_radius(current_data)))
            current_data = {"name": row[2:]}
        else:
            variable, value = row.split(":")
            variable = variable.strip()
            if "," in value:
                value = [float(v.strip()) for v in value.split(",") if v.strip()]
            else:
                value = Length(
                    *(
                        int(v)
                        if set(v).issubset("0123456789")
                        else float(v)
                        if set(v).issubset("0123456789.")
                        else v
                        for v in value.split(" ")
                        if v
                    )
                )
            current_data[variable] = value
    if current_data:
        bikes.append(Bike(**get_full_radius(current_data)))

    return bikes


def to_x(width, value, max_value):
    return math.log(value) / math.log(max_value) * width * 0.95 + 0.02


def show(size, aa, bikes, image_file=None):
    draw_size = (size[0] * aa, size[1] * aa)

    def p(x) -> int:
        """Convert from percent of total height to pixels."""
        return round(draw_size[1] * x / 100)

    radius = p(1)
    pygame.init()
    label_font = pygame.font.Font(None, p(4))
    name_font = pygame.font.Font(None, p(2))
    S = pygame.display.set_mode(size)
    pygame.display.set_caption("Gears")

    image = pygame.Surface(draw_size)
    image.fill(BACK_COLOUR)
    ratios = [b.get_gain_ratios() for b in bikes]
    max_ratio = max(max(x) for x in ratios)[0]
    # Draw lines
    for i in range(1, 200):
        i /= 10
        x = to_x(draw_size[0], i, max_ratio)
        if x > draw_size[0] * 1.1:
            break

        thickness = p((0.03 if i % 0.5 else 0.1 if i % 1 else 0.3))
        pygame.draw.line(
            image, LINE_COLOUR, (round(x), 0), (round(x), draw_size[1]), thickness
        )
        if not i % 1:
            label = label_font.render(str(round(i)), True, LINE_COLOUR)
            image.blit(
                label, (round(x - label.get_width() - draw_size[1] * 0.003), p(1))
            )

    # Draw bikes
    for index, (bike, ratio_list) in enumerate(zip(bikes, ratios)):
        y = draw_size[1] * (index + 1) / (len(bikes) + 1)
        position = 1
        forced_pos = True
        for ratio, gears in ratio_list:
            front_diff = gears[0] - len(bike.front) / 2 - 0.5
            rear_diff = gears[1] - len(bike.rear) / 2 - 0.5
            this_y = y + draw_size[1] * 0.03 * front_diff
            x = to_x(draw_size[0], ratio, max_ratio)
            drawpos = (round(x), round(this_y))
            is_gear_bad = (len(bike.rear) - 1) * 0.25 <= abs(rear_diff) * abs(
                front_diff
            ) and rear_diff * front_diff < 0
            pygame.draw.circle(
                image, BLOB_COLOUR, drawpos, round(radius), is_gear_bad * p(0.2)
            )

            label = name_font.render(
                f"{gears[0]}–{gears[1]}" if len(bike.front) > 1 else str(gears[1]),
                True,
                LABEL_COLOUR,
            )
            if gears[0] > len(bike.front) / 2 + 0.5:
                position = 1
                forced_pos = True
            elif gears[0] < len(bike.front) / 2 + 0.5:
                position = -1
                forced_pos = True
            else:
                if forced_pos:
                    position = -position
                forced_pos = False
            text_y = (
                this_y
                - label.get_height() / 2
                + position * (label.get_height() / 2 + radius * 1.1)
            )
            image.blit(label, (round(x - label.get_width() / 2), round(text_y)))
        label = label_font.render(bike.name, True, LABEL_COLOUR)
        image.blit(label, (p(2), round(y - label.get_height() / 2)))
    S.blit(image if aa == 1 else pygame.transform.smoothscale(image, size), (0, 0))
    if image_file is not None:
        pygame.image.save(S, image_file.name)
    ext = False
    clock = pygame.time.Clock()
    while not ext:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ext = True
                break
        pygame.display.flip()
        clock.tick(20)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bikes", type=argparse.FileType("r"), help="bike gears data file"
    )
    parser.add_argument("-x", "--width", type=int, help="window width", default=1280)
    parser.add_argument("-y", "--height", type=int, help="window height", default=720)
    parser.add_argument(
        "-s",
        "--supersampling",
        type=int,
        help="amount of supersamping antialiasing to use",
        default=16,
    )
    parser.add_argument(
        "-o",
        "--output-image",
        type=argparse.FileType("wb"),
        help="image file to output to",
    )
    args = parser.parse_args()
    bikes = load_bikes(args.bikes)
    show(
        (args.width, args.height),
        args.supersampling,
        bikes,
        image_file=args.output_image,
    )


if __name__ == "__main__":
    main()

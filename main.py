import curses
import random
import time
from typing import List

BOARD = ["┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨",
         "┃   │   │   ┃   │   │   ┃   │   │   ┃",
         "┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛"]


class Field:

    def __init__(self, row, column) -> None:
        self.row = row
        self.column = column
        self.group = self.calc_group()
        self.possible_vals = [*range(1, 10)]
        self.value = 0

    def entropy(self) -> int:
        return len(self.possible_vals)

    def set_random_value_from_possible_values(self):
        if self.value == 0:
            value = random.choice(self.possible_vals)
            self.possible_vals = []
            self.value = value

    def remove_possible_value(self, value: int):
        if value in self.possible_vals:
            self.possible_vals.remove(value)

    def get_value(self) -> str:
        if self.value == 0:
            return " "
        else:
            return str(self.value)

    def screen_line(self) -> int:
        return self.row * 2 + 1

    def screen_column(self) -> int:
        return self.column * 4 + 2

    def calc_group(self):
        if self.row <= 2 and self.column <= 2:
            return 0
        if self.row <= 2 and self.column <= 5:
            return 1
        if self.row <= 2 and self.column <= 8:
            return 2
        if self.row <= 5 and self.column <= 2:
            return 3
        if self.row <= 5 and self.column <= 5:
            return 4
        if self.row <= 5 and self.column <= 8:
            return 5
        if self.row <= 8 and self.column <= 2:
            return 6
        if self.row <= 8 and self.column <= 5:
            return 7
        if self.row <= 8 and self.column <= 8:
            return 8


class Board:

    def __init__(self, screen) -> None:
        self.screen = screen

        self.errors = []

        self.fields: List[Field] = []
        self.no_fields_with_value = 0

        for i in range(0, 9):
            for j in range(0, 9):
                self.fields.append(Field(i, j))

    def set_random_fields(self):
        chosen_fields = []
        for i in range(0, 9):
            group = [f for f in self.fields if f.group == i]
            random.shuffle(group)
            if random.randint(0, 2) == 0:
                chosen_fields.append(group[0])
            if random.randint(0, 10) == 0:
                chosen_fields.append(group[1])

        for field in chosen_fields:
            self.set_field_value(field)

        self.screen.refresh()

    def find_errors(self):
        self.errors = []
        for i in range(0, 9):
            row = [f for f in self.fields if f.row == i]
            column = [f for f in self.fields if f.column == i]
            group = [f for f in self.fields if f.group == i]

            if sum([field.value for field in row]) != 45:
                self.errors.append(f"error in row {i}")

            if sum([field.value for field in column]) != 45:
                self.errors.append(f"error in column {i}")

            if sum([field.value for field in group]) != 45:
                self.errors.append(f"error in group {i}")

    def draw_board(self):
        curses.use_default_colors()
        # curses.curs_set(0)
        self.screen.clear()
        pad = curses.newpad(19, 37)

        i = 0
        for board_line in BOARD:
            self.screen.addstr(i, 0, board_line)
            i += 1

        self.screen.refresh()

    def draw_field(self, field: Field):
        self.screen.addch(field.screen_line(),
                          field.screen_column(),
                          field.get_value())
        self.screen.refresh()

    def choose_random_field_with_smallest_entropy(self) -> Field:
        fields_min_entropy = []
        min_entropy = 0
        for field in self.fields:
            if field.entropy() == 0:
                continue
            elif min_entropy == 0:
                min_entropy = field.entropy()

            if field.entropy() == min_entropy:
                fields_min_entropy.append(field)
            else:
                break

        return random.choice(fields_min_entropy)

    def propagate(self, propagated_field: Field):
        for field in self.fields:
            if field.row == propagated_field.row and field.column == propagated_field.column:
                continue

            if field.row == propagated_field.row or field.column == propagated_field.column or field.group == propagated_field.group:
                field.remove_possible_value(propagated_field.value)

            if len(field.possible_vals) == 1:
                self.set_field_value(field)

        self.fields.sort(key=lambda f: f.entropy())

    def set_field_value(self, field: Field):
        field.set_random_value_from_possible_values()
        self.no_fields_with_value += 1
        self.propagate(field)
        self.draw_field(field)

    def solve(self):
        time.sleep(1)
        while self.no_fields_with_value < 81:
            time.sleep(0.1)
            rand_field = self.choose_random_field_with_smallest_entropy()
            self.set_field_value(rand_field)

        self.screen.refresh()
        self.screen.getkey()

        sum = 0
        for field in self.fields:
            sum += field.value

        # if sum != 405:
        #     self.find_errors()
        #     print(sum)


def main(stdscr):
    board = Board(stdscr)
    board.draw_board()
    board.set_random_fields()
    board.solve()


if __name__ == "__main__":
    curses.wrapper(main)

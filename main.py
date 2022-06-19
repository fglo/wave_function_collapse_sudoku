import curses
import random
import time
from typing import List

class Field:
    
    def __init__(self, row, column) -> None:
        self.row = row
        self.column = column
        self.group = self.calc_group()
        self.possible_vals = [*range(1, 10)]
        self.value = 0
        
    def entropy(self) -> int:
        return len(self.possible_vals)
    
    def set_value(self, value: int):
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
            return 1
        if self.row <= 2 and self.column <= 5:
            return 2
        if self.row <= 2 and self.column <= 8:
            return 3
        if self.row <= 5 and self.column <= 2:
            return 4
        if self.row <= 5 and self.column <= 5:
            return 5
        if self.row <= 5 and self.column <= 8:
            return 6
        if self.row <= 8 and self.column <= 2:
            return 7
        if self.row <= 8 and self.column <= 5:
            return 8
        if self.row <= 8 and self.column <= 8:
            return 9
    
class Board:
    
    def __init__(self, screen) -> None:
        self.screen = screen
        self.fields: List[Field] = []
        
        for i in range(0, 9):
            for j in range(0, 9):
                self.fields.append(Field(i, j))

    def set_random_fields(self):
        chosen_fields = []
        for i in range(1, 10):
            group = [f for f in self.fields if f.group == i]
            random.shuffle(group)
            if random.randint(0, 2) == 0: 
                chosen_fields.append(group[0])
            if random.randint(0, 10) == 0: 
                chosen_fields.append(group[1])

        for field in chosen_fields:
            self.set_field_value(field)
            
        self.screen.refresh()

    def draw_board(self):
        self.screen.clear()

        with open('board', 'r') as board_file:
            lines = board_file.readlines()
            i = 0
            for line in lines:
                self.screen.addstr(i, 0, line.replace("\n", ""))
                i += 1
        
        self.screen.refresh() 
    
    def draw_field(self, field: Field):
        self.screen.addch(field.screen_line(), field.screen_column(), field.get_value())
        self.screen.refresh()
    
    def choose_random_field_with_smallest_entropy(self) -> Field:
        i = 0
        min_entropy = self.fields[0].entropy()
        for field in self.fields:
            if field.entropy() == min_entropy:
                i += 1
            else:
                break
                
        return random.choice(self.fields[0:i+1])
    
    def propagate_in_row(self, propagated_field: Field):
        for field in self.fields:
            if field.row == propagated_field.row and propagated_field.value in field.possible_vals:
                field.possible_vals.remove(propagated_field.value)
            
    def propagate_in_column(self, propagated_field: Field):
        for field in self.fields:
            if field.column == propagated_field.column and propagated_field.value in field.possible_vals:
                field.possible_vals.remove(propagated_field.value)
    
    def propagate_in_group(self, propagated_field: Field):        
        for field in self.fields:
            if field.group == propagated_field.group and propagated_field.value in field.possible_vals:
                field.possible_vals.remove(propagated_field.value)
    
    def propagate(self, propagated_field: Field):
        self.fields.remove(propagated_field)
        
        for field in self.fields:
            if field.row == propagated_field.row and field.column == propagated_field.column:
                continue
            
            if field.row == propagated_field.row and propagated_field.value in field.possible_vals:
                field.possible_vals.remove(propagated_field.value)
            elif field.column == propagated_field.column and propagated_field.value in field.possible_vals:
                field.possible_vals.remove(propagated_field.value)
            elif field.group == propagated_field.group and propagated_field.value in field.possible_vals:
                field.possible_vals.remove(propagated_field.value)
                
            if len(field.possible_vals) == 1:
                self.set_field_value(field)
        
        self.fields.sort(key=lambda f: f.entropy())
    
    def set_field_value(self, field: Field):
            field.set_value(random.choice(field.possible_vals))
            self.propagate(field)
            self.draw_field(field)
    
    def solve(self):
        time.sleep(1)
        while len(self.fields) > 0:
            time.sleep(0.1)
            rand_field = self.choose_random_field_with_smallest_entropy()
            self.set_field_value(rand_field)
    
        curses.curs_set(0)   
        
        self.screen.refresh()
        self.screen.getkey()
        
        
def main(stdscr):     
    board = Board(stdscr)
    board.draw_board()  
    board.set_random_fields()
    board.solve()

if __name__ == "__main__":
    curses.wrapper(main)
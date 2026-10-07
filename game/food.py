import pygame
import random

class Food:
    def __init__(self, grid_width, grid_height, cell_size):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.x = 0
        self.y = 0
        self.respawn([])

    def respawn(self, occupied_cells):
        available_cells = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in occupied_cells
        ]
        if not available_cells:
            return False

        self.x, self.y = random.choice(available_cells)
        return True

    def rect(self):
        return pygame.Rect(self.x * self.cell_size, self.y * self.cell_size, self.cell_size, self.cell_size)

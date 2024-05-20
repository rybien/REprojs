#!/usr/bin/env python
# coding: utf-8

# In[20]:


# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 08:42:20 2024

@author: 24RBienstock
"""

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from enum import Enum

class SquareType:
    REGULAR = 1
    GOODWEATHER = 2
    KRAKEN_SPAWN = 3
    DISABLE = 4

class GameBoard:
    def __init__(self, size=10, krakens=2, kraken_spawn_points=2, goodweather_squares=3, disable_squares=3):
        self.size = size
        self.board = [[SquareType.REGULAR for _ in range(size)] for _ in range(size)]
        self._place_special_squares(kraken_spawn_points, goodweather_squares, disable_squares)
        self.krakens = [{'x': None, 'y': None} for _ in range(krakens)]
        self._place_krakens()

    def _place_special_squares(self, kraken_spawn_points, goodweather_squares, disable_squares):
        self._place_square_type(SquareType.KRAKEN_SPAWN, kraken_spawn_points)
        self._place_square_type(SquareType.GOODWEATHER, goodweather_squares)
        self._place_square_type(SquareType.DISABLE, disable_squares)

    def _place_square_type(self, square_type, count):
        for _ in range(count):
            while True:
                x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
                if self.board[x][y] == SquareType.REGULAR:
                    self.board[x][y] = square_type
                    break

    def _place_krakens(self):
        for kraken in self.krakens:
            while True:
                x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
                if self.board[x][y] == SquareType.REGULAR:
                    kraken['x'], kraken['y'] = x, y
                    break
def print_special_square_locations(board):
    goodweather_locations = []
    kraken_spawn_locations = []
    disable_locations = []

    for x, row in enumerate(board):
        for y, square_type in enumerate(row):
            if square_type == SquareType.GOODWEATHER:
                goodweather_locations.append((y, x))
            elif square_type == SquareType.KRAKEN_SPAWN:
                kraken_spawn_locations.append((y, x))
            elif square_type == SquareType.DISABLE:
                disable_locations.append((y, x))
    print("Goodweather Square Locations:", goodweather_locations)
    print("Kraken Spawn Point Locations:", kraken_spawn_locations)
    print("Disable Square Locations:", disable_locations)
    return goodweather_locations, kraken_spawn_locations, disable_locations
    


class Ship:
    def __init__(self, board_size):
        self.x = 0  # Start at top left
        self.y = 0
        self.goodweather_turns_left = 0
        self.board_size = board_size

    def shipMove(self, direction, board):
        if self.goodweather_turns_left > 0:
            step_size = 2
            self.goodweather_turns_left -= 1
        else:
            step_size = 1

        # Wind effect applies only if not under Goodweather influence
        if random.random() < 0.15 and self.goodweather_turns_left == 0:
            direction = self._get_opposite_direction(direction)
            print("Wind!")

        dx, dy = self._direction_to_delta(direction, step_size)
        self.x, self.y = self._apply_movement(self.x + dx, self.y + dy)

        

    def _direction_to_delta(self, direction, step_size):
        return {
            "up": (0, -step_size),
            "down": (0, step_size),
            "left": (-step_size, 0),
            "right": (step_size, 0)
        }.get(direction, (0, 0))  # Default to no movement if direction is invalid

    def _get_opposite_direction(self, direction):
        return {"up": "down", "down": "up", "left": "right", "right": "left"}.get(direction, direction)

    def _apply_movement(self, x, y):
        x = max(0, min(self.board_size - 1, x))
        y = max(0, min(self.board_size - 1, y))
        return x, y

    def _apply_disable_effect(self):
        directions = ["up", "down", "left", "right"]
        random_direction = random.choice(directions)
        dx, dy = self._direction_to_delta(random_direction, 3)
        self.x, self.y = self._apply_movement(self.x + dx, self.y + dy)


class Kraken:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def KrakenMove(self, board, board_size):
        move_options = [(3, 2), (3, -2), (-3, 2), (-3, -2), (2, 3), (2, -3), (-2, 3), (-2, -3)]
        dx, dy = random.choice(move_options)
        self.x = max(0, min(board_size - 1, self.x + dx))
        self.y = max(0, min(board_size - 1, self.y + dy))
        # Check if landed on kraken spawn point
        if board[self.x][self.y] == SquareType.KRAKEN_SPAWN:
            # Move kraken to top middle and spawn a new kraken at bottom middle
            self.x, self.y = board_size // 2, 0
            board[board_size // 2][board_size - 1] = SquareType.KRAKEN_SPAWN  # New kraken spawn logic
            

"""
Regular Square: Light blue
Goodweather Square: Red
Kraken Spawn Point: Gray
Disable Square: Yellow
Ship: Black
Kraken: Green"""

def draw_board(board, ship, krakens):
    # Create a numeric board representation including ship (5) and krakens (6)
    numeric_board = [[board[x][y] for y in range(len(board))] for x in range(len(board))]
    numeric_board[ship.y][ship.x] = 5  # Mark the ship's position with code 5
    for kraken in krakens:
        numeric_board[kraken.y][kraken.x] = 6  # Mark kraken positions with code 6

    # Define a custom colormap with an additional color for krakens
    cmap = mcolors.ListedColormap(['white', 'lightblue', 'red', 'gray', 'yellow', 'black', 'green'])
    # Update bounds for the new numeric codes including an extra color for krakens
    bounds = [0, 1, 2, 3, 4, 5, 6, 7]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(numeric_board, cmap=cmap, norm=norm)

    # Customize ticks and labels (optional)
    ax.set_xticks(range(len(board[0])))
    ax.set_yticks(range(len(board)))
    ax.set_xticklabels(range(len(board[0])))
    ax.set_yticklabels(range(len(board)))
    plt.grid(which='both', color='lightgrey', linestyle='-', linewidth=0.5)
    plt.show()



def run_game():
    board_size = 10
    attempts = 1
    game_board = GameBoard(size=board_size)
    ship = Ship(board_size=board_size)
    krakens = [Kraken(k['x'], k['y']) for k in game_board.krakens]

    while True:
        draw_board(game_board.board, ship, krakens)
        print(f"Ship's current position: ({ship.x}, {ship.y}). Attempts: {attempts}")
        print("Kraken locations:", [(kraken.x, kraken.y) for kraken in krakens])
        goodweather_locations, kraken_spawn_locations, disable_locations = print_special_square_locations(game_board.board)
        direction = input("Enter movement direction (up, down, left, right): ").strip().lower()

        ship.shipMove(direction, game_board.board)
        ship_position = (ship.x, ship.y)
        #attempts += 1
        # Check the square the ship lands on
        #square_type = game_board.board[ship.x][ship.y]
        #print(f"Current Square Type: {square_type}")
        if ship_position in goodweather_locations:
            print("Landed on a Goodweather square! Next three moves will be safe from wind and move double spaces.")
            ship.goodweather_turns_left = 3
        elif ship_position in disable_locations:
            print("Landed on a Disable square! Moving 3 squares in a random cardinal direction.")
            ship._apply_disable_effect()
        # Check for kraken encounter
        for i, kraken in enumerate(krakens):
            kraken.KrakenMove(game_board.board, board_size)
            if kraken.x == ship.x and kraken.y == ship.y:
                print("A kraken has caught the ship! Restarting...")
                ship = Ship(board_size=board_size)  # Ship goes back to start
                attempts += 1
                break

            # Check for kraken collision
            for j, other_kraken in enumerate(krakens):
                if i != j and kraken.x == other_kraken.x and kraken.y == other_kraken.y:
                    print("Two krakens have collided! One disappears.")
                    del krakens[j]
                    break

        if ship.x == board_size - 1 and ship.y == board_size - 1:
            print(f"Congratulations! You've reached the goal in {attempts} attempts.")
            break

    
    
if __name__ == "__main__":
    run_game()
    

"""
Regular Square: Light blue
Goodweather Square: Red
Kraken Spawn Point: Gray
Disable Square: Yellow
Ship: Black
Kraken: Green"""


# In[ ]:





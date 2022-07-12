# Myriam KIRIAKOS 1888929
# Marco NOVAES 2166579

from tkinter import S
import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.lines import Line2D
import numpy as np
import random

import math
import copy

GRAY = 0
BLACK = 23
RED = 24
WHITE = 25

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3


class EternityPuzzle:

    def __init__(self, instance_file):

        with open(instance_file) as file:
            lines = file.readlines()

            self.board_size = int(lines[0])
            self.n_piece = self.board_size ** 2
            self.n_internal_connection = 2 * self.board_size * (self.board_size - 1)
            self.n_total_connection = self.n_internal_connection + self.board_size * 4

            flatten = lambda l: [item for sublist in l for item in sublist]

            self.piece_list = [(int(x.split()[0]), int(x.split()[1]), int(x.split()[2]), int(x.split()[3])) for line in
                               lines[1:] for x in line.strip().split('\n')]

            self.n_color = max(flatten(self.piece_list)) + 1

            assert (len(self.piece_list) == self.n_piece)

            for p in self.piece_list:
                assert (len(p) == 4)

    def generate_rotation(self, piece):

        initial_shape = piece
        rotation_90 = (piece[2], piece[3], piece[1], piece[0])
        rotation_180 = (piece[1], piece[0], piece[3], piece[2])
        rotation_270 = (piece[3], piece[2], piece[0], piece[1])

        return [initial_shape, rotation_90, rotation_180, rotation_270]

    def generate_random_rotation(self, piece):
        rotation = random.randint(1,4)
        if rotation == 1:
            return piece
        if rotation == 2:
            return (piece[2], piece[3], piece[1], piece[0])
        if rotation == 3:
            return (piece[1], piece[0], piece[3], piece[2])
        if rotation == 4:
            return (piece[3], piece[2], piece[0], piece[1])

    def get_total_n_conflict(self, solution):

        n_conflict = 0

        for j in range(self.board_size):
            for i in range(self.board_size):
                # j ligne, i colonne
                # sud vers haut
                # est vers la gauche
                k = self.board_size * j + i
                k_east = self.board_size * j + (i - 1)
                k_south = self.board_size * (j - 1) + i

                if i > 0 and solution[k][WEST] != solution[k_east][EAST]:
                    n_conflict += 1

                if i == 0 and solution[k][WEST] != GRAY:
                    n_conflict += 1

                if i == self.board_size - 1 and solution[k][EAST] != GRAY:
                    n_conflict += 1

                if j > 0 and solution[k][SOUTH] != solution[k_south][NORTH]:
                    n_conflict += 1

                if j == 0 and solution[k][SOUTH] != GRAY:
                    n_conflict += 1

                if j == self.board_size - 1 and solution[k][NORTH] != GRAY:
                    n_conflict += 1

        return n_conflict

    def get_local_n_conflict(self, k, solution):
        """
        :return : number of conflicts for piece `k` in `solution`
        """
        n_conflict = 0    
        i = k % self.board_size
        j = k // self.board_size

        k_rigth = k + 1
        k_down = k - self.board_size
        k_up = k + self.board_size
        k_left = k - 1

        # The "!= -1" condition in if statements is to ignore non-assigned neighboors (see the destroy function in solver_advanced)

        # north
        if j == self.board_size - 1: 
            if solution[k][NORTH] != GRAY:
                n_conflict += 1
        else:
            if solution[k][NORTH] != solution[k_up][SOUTH] and solution[k_up][SOUTH] != -1:
                n_conflict += 1

        # south
        if j == 0: 
            if solution[k][SOUTH] != GRAY:
                n_conflict += 1
        else:
            if solution[k][SOUTH] != solution[k_down][NORTH] and solution[k_down][NORTH] != -1:
                n_conflict += 1

        # east
        if i == self.board_size - 1: 
            if solution[k][EAST] != GRAY:
                n_conflict += 1
        else:
            if solution[k][EAST] != solution[k_rigth][WEST] and solution[k_rigth][WEST] != -1:
                n_conflict += 1

        # west
        if i == 0: 
            if solution[k][WEST] != GRAY:
                n_conflict += 1
        else:
            if solution[k][WEST] != solution[k_left][EAST] and solution[k_left][EAST] != -1:
                n_conflict += 1

        return n_conflict

    def exist_conflict_between_pieces(self, k1, k2, solution):
        """
        :return : exist_conflict_between_pieces, areNeighbours
        """

        # j ligne, i colonne

        i1 = k1 % self.board_size
        j1 = k1 // self.board_size

        i2 = k2 % self.board_size
        j2 = k2 // self.board_size


        # piece2 under piece1
        if i1==i2 and j1-1 == j2:
            if solution[k1][SOUTH] != solution[k2][NORTH]:
                return True, True
            else:
                return False, True
            
        # piece2 above piece1
        if i1==i2 and j1+1 == j2:
            if solution[k1][NORTH] != solution[k2][SOUTH]:
                return True, True
            else:
                return False, True

        # piece2 to the left of piece1
        if j1==j2 and i1-1 == i2:
            if solution[k1][WEST] != solution[k2][EAST]:
                return True, True
            else:
                return False, True

        # piece2 to the right of piece1
        if j1==j2 and i1+1 == i2:
            if solution[k1][EAST] != solution[k2][WEST]:
                return True, True
            else:
                return False, True

        return False, False

    def display_solution(self, solution, output_file):

        if len(solution) < self.n_piece:
            solution = solution + [(WHITE, WHITE, WHITE, WHITE)] * (self.n_piece - len(solution))

        origin = 0
        size = self.board_size + 2

        color_dict = self.build_color_dict()

        fig, ax = plt.subplots()

        n_total_conflict = self.get_total_n_conflict(solution)

        n_internal_conflict = 0

        for j in range(size):  # y-axis
            for i in range(size):  # x-axis
                valid_draw = [0, size - 1]
                if i in valid_draw or j in valid_draw:
                    ax.add_patch(patches.Rectangle((i, j), i + 1, j + 1, fill=True, facecolor=color_dict[GRAY],
                                                   edgecolor=color_dict[BLACK]))
                else:
                    # ax.add_patch(patches.Rectangle((i, j), i + 1, j + 1, fill=True, facecolor='white', edgecolor='k'))

                    left_bot = (i, j)
                    right_bot = (i + 1, j)
                    right_top = (i + 1, j + 1)
                    left_top = (i, j + 1)
                    middle = (i + 0.5, j + 0.5)

                    instructions = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]

                    triangle_south_path = Path([left_bot, middle, right_bot, left_bot], instructions)
                    triangle_east_path = Path([right_top, middle, right_bot, right_top], instructions)
                    triangle_north_path = Path([right_top, middle, left_top, right_top], instructions)
                    triangle_west_path = Path([left_bot, middle, left_top, left_bot], instructions)

                    is_triangle_south_valid = True
                    is_triangle_north_valid = True
                    is_triangle_east_valid = True
                    is_triangle_west_valid = True

                    k = self.board_size * (j - 1) + (i - 1)
                    k_east = self.board_size * (j - 1) + (i - 2)
                    k_south = self.board_size * (j - 2) + (i - 1)

                    if i == 1:
                        is_triangle_west_valid = (solution[k][WEST] == GRAY)  # 1 for Gray
                    elif i == size - 2:
                        is_triangle_east_valid = (solution[k][EAST] == GRAY)
                        is_triangle_west_valid = solution[k][WEST] == solution[k_east][EAST]
                    else:
                        is_triangle_west_valid = solution[k][WEST] == solution[k_east][EAST]

                    if j == 1:
                        is_triangle_south_valid = (solution[k][SOUTH] == GRAY)
                    elif j == size - 2:
                        is_triangle_north_valid = (solution[k][NORTH] == GRAY)
                        is_triangle_south_valid = solution[k][SOUTH] == solution[k_south][NORTH]
                    else:
                        is_triangle_south_valid = solution[k][SOUTH] == solution[k_south][NORTH]

                    patch_south = patches.PathPatch(triangle_south_path, facecolor=color_dict[solution[k][SOUTH]],
                                                    edgecolor=color_dict[BLACK])

                    patch_north = patches.PathPatch(triangle_north_path, facecolor=color_dict[solution[k][NORTH]],
                                                    edgecolor=color_dict[BLACK])

                    patch_east = patches.PathPatch(triangle_east_path, facecolor=color_dict[solution[k][EAST]],
                                                   edgecolor=color_dict[BLACK])

                    patch_west = patches.PathPatch(triangle_west_path, facecolor=color_dict[solution[k][WEST]],
                                                   edgecolor=color_dict[BLACK])

                    if not is_triangle_south_valid:
                        line_zip = list(zip(left_bot, right_bot))
                        line = Line2D(line_zip[0], line_zip[1], color=color_dict[RED], lw=3)
                        ax.add_line(line)

                        if j != 1:
                            n_internal_conflict += 1

                    if not is_triangle_north_valid:
                        line_zip = list(zip(left_top, right_top))
                        line = Line2D(line_zip[0], line_zip[1], color=color_dict[RED], lw=3)
                        ax.add_line(line)

                        if j != size - 2:
                            n_internal_conflict += 1

                    if not is_triangle_west_valid:
                        line_zip = list(zip(left_bot, left_top))
                        line = Line2D(line_zip[0], line_zip[1], color=color_dict[RED], lw=3)
                        ax.add_line(line)

                        if i != 1:
                            n_internal_conflict += 1

                    if not is_triangle_east_valid:
                        line_zip = list(zip(right_bot, right_top))
                        line = Line2D(line_zip[0], line_zip[1], color=color_dict[RED], lw=3)
                        ax.add_line(line)

                        if i != size - 2:
                            n_internal_conflict += 1

                    ax.add_patch(patch_south)
                    ax.add_patch(patch_north)
                    ax.add_patch(patch_east)
                    ax.add_patch(patch_west)

                    k += 1

        plt.xlim(origin, size)
        plt.ylim(origin, size)

        title = 'Eternity of size %d X %d\n' \
                'Total connections: %d    Internal connections: %d\n' \
                'Total Valid connections: %d     Internal valid internal connections: %d\n' \
                'Total Invalid connections: %d    Internal invalid connections: %d' % \
                (self.board_size, self.board_size,
                 self.n_total_connection, self.n_internal_connection,
                 self.n_total_connection - n_total_conflict, self.n_internal_connection - n_internal_conflict,
                 n_total_conflict, n_internal_conflict,
                 )
        ax.set_title(title)

        plt.savefig(output_file)

    def print_solution(self, solution, output_file):
        with open(output_file, "w") as file:
            file.write(str(self.get_total_n_conflict(solution)) + "\n")
            file.write(str(self.board_size))
            for piece in solution:
                file.write("\n")
                for c in piece:
                    file.write(str(c) + " ")

    def build_color_dict(self):

        color_dict = {
            GRAY: 'gray',
            1: 'lightcoral',
            2: 'tab:blue',
            3: 'tab:orange',
            4: 'tab:green',
            5: 'gold',
            6: 'tab:purple',
            7: 'tab:brown',
            8: 'tab:pink',
            9: 'tab:olive',
            10: 'tab:cyan',
            11: 'deeppink',
            12: 'blue',
            13: 'slateblue',
            14: 'darkslateblue',
            15: 'darkviolet',
            16: 'teal',
            17: 'wheat',
            18: 'darkkhaki',
            19: 'indigo',
            20: 'fuchsia',
            21: 'lime',
            22: 'rosybrown',
            BLACK: 'black',
            RED: 'tab:red',
            WHITE: 'white'
        }
        return color_dict

    def hash_piece(self, piece):
        all = self.generate_rotation(piece)
        return min(all)

    def verify_solution(self,solution):
        hash_init = sorted([self.hash_piece(p) for p in self.piece_list])
        hash_sol = sorted([self.hash_piece(p) for p in solution])

        return hash_init == hash_sol


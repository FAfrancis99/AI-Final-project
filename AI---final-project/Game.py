
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import os
import random
import time
import utils

class Game:
    def __init__(self, board, players_positions, max_dust_score,
                 dust_max_part_of_free_spaces=0.2,
                 animated=False, animation_func=None):
        """Initialize the game properties with parameters."""
        assert len(players_positions) == 2, 'Supporting 2 players only'
        self.map = board
        self.max_dust_score = max_dust_score
        self.min_dust_time = min(len(board[0]), len(board))

        self.dust_max_part_of_free_spaces = dust_max_part_of_free_spaces
        self.players_positions = players_positions
        self.players_score = [0, 0]
        self.directions = utils.get_directions()
        dust_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fruits_imgs')
        self.dust_paths = [os.path.join(dust_dir, dust_file) for dust_file in os.listdir(dust_dir)]
        self.dust_on_board = {}

        self.turn = 0

        self.animated = animated
        self.animation_func = animation_func

        if self.animated:
            self.init_animation()
        self.create_dust()
        self.players_positions = [tuple(reversed(position)) for position in self.players_positions]

    def init_animation(self):
        """Initialize animation setup."""
        # Set the Matplotlib backend to TkAgg or another GUI backend that opens new windows
        plt.switch_backend('TkAgg')

        # Colors:
        self.board_colors = {'free': 'gray', 'stepped on': 'gray'}
        self.players_colors = ['blue', 'red']

        aspect = len(self.map[0]) / len(self.map)
        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=None, hspace=None)

        # create boundary patch
        x_min, y_min = -0.5, -0.5
        x_max = len(self.map[0]) - 0.5
        y_max = len(self.map) - 0.5
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        # patches = board_patch + map_patches + player_patches
        self.board_patch = [Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, facecolor='none', edgecolor='gray')]
        self.map_patches = []
        for i in range(len(self.map)):
            self.map_patches.append([])
            for j in range(len(self.map[0])):
                if self.map[i][j] != 0:
                    face_color = self.board_colors['stepped on']
                    self.map_patches[i].append(
                        Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=face_color, edgecolor='black', fill=True))
                else:
                    face_color = self.board_colors['free']
                    self.map_patches[i].append(
                        Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=face_color, edgecolor='black', fill=False))

        # painting the starting positions of the players:
        self.map_patches[self.players_positions[0][0]][self.players_positions[0][1]].fill = True
        self.map_patches[self.players_positions[1][0]][self.players_positions[1][1]].fill = True

        # create players:
        self.T = 0
        self.players = []
        self.player_patches = []
        for i in range(len(self.players_positions)):
            self.players.append(
                Circle(tuple(reversed(self.players_positions[i])), 0.3, facecolor=self.players_colors[i],
                       edgecolor='black'))
            self.players[i].original_face_color = self.players_colors[i]
            self.player_patches.append(self.players[i])
            self.T = max(self.T, len(self.players_positions[i]) - 1)

        global animation
        animation = FuncAnimation(self.fig, self.animation_func,
                                  init_func=self.init_func,
                                  frames=int(self.T + 1) * 10,
                                  interval=600,
                                  blit=False)

    @staticmethod
    def start_game():
        """Start the game animation."""
        plt.show()

    def init_func(self):
        for p in self.board_patch + sum(self.map_patches, []) + self.player_patches:
            self.ax.add_patch(p)
        return self.board_patch + sum(self.map_patches, []) + self.players

    def update_map(self, prev_pos, next_pos):
        player_id = self.map[prev_pos[1]][prev_pos[0]]
        self.map[prev_pos[1]][prev_pos[0]] = -1
        self.map[next_pos[1]][next_pos[0]] = player_id

    def choose_dust_pos(self):
        # get all free places on board
        free_places = np.where(self.map == 0)
        if len(free_places[0]) == 0:
            return -1

        idx = random.randint(0, len(free_places[0]) - 1)

        pos = (free_places[0][idx], free_places[1][idx])

        return pos  # pos on self.map (reversed in animation)

    def remove_dust_from_board(self, pos):
        if self.map[pos[0], pos[1]] == self.dust_on_board[pos]['value']:  # don't override a player if exists there. Safety first!
            self.map[pos[0], pos[1]] = 0

        if self.animated:
            dust_art = self.dust_on_board[pos]['fruit_art']
            dust_art.remove()
        del self.dust_on_board[pos]

    def add_dust(self, pos):
        if self.animated:
            dust_idx = random.randint(0, len(self.dust_paths) - 1)
            dust_path = self.dust_paths[dust_idx]
            img = plt.imread(dust_path)
            off_img = OffsetImage(img, zoom=0.3)
            bbox = AnnotationBbox(off_img, (pos[1], pos[0]), frameon=False)
            dust = self.ax.add_artist(bbox)
        else:
            dust = None
        value = 50
        # value = random.randint(3, self.max_dust_score)
        self.map[pos[0], pos[1]] = value
        self.dust_on_board[pos] = {'fruit_art': dust, 'value': value}

    def create_dust(self):
        num_free_places = len(np.where(self.map == 0)[0])
        if num_free_places != 0:
            num_fruits = random.randint(0, int(num_free_places * self.dust_max_part_of_free_spaces))
            # add new fruits in free spaces (not occupied by players, fruits, blocked cells)
            for _ in range(num_fruits):
                pos = self.choose_dust_pos()  # don't cover the players, existing fruits and blocked cells
                if pos != -1:
                    self.add_dust(pos)


    def update_player_pos(self, pos):
        prev_pos = self.players_positions[self.turn]

        # update the scores of the player
        if self.map[pos[1]][pos[0]] > 2:
            # update score value for player
            self.players_score[self.turn] += self.map[pos[1]][pos[0]]
            # remove dust from board
            self.remove_dust_from_board(tuple(reversed(pos)))

        # update patch/position of player
        self.players_positions[self.turn] = pos

        if self.animated:
            self.players[self.turn].center = pos

            i = pos[1]
            j = pos[0]
            self.map_patches[i][j].fill = True

        return prev_pos

    def update_staff_with_pos(self, pos):
        pos = tuple(reversed(pos))
        prev_pos = self.update_player_pos(pos)
        self.update_map(prev_pos=prev_pos, next_pos=pos)
        # self.update_dust()

        self.turn = 1 - self.turn
        if self.animated:
            return self.board_patch + sum(self.map_patches, []) + self.players

    def player_cant_move(self, player_id):
        player_pos = self.get_player_position(player_id)
        all_next_positions = [utils.tup_add(player_pos, direction) for direction in self.directions]
        possible_next_positions = [pos for pos in all_next_positions if self.pos_feasible_on_board(pos)]
        return len(possible_next_positions) == 0

    def pos_feasible_on_board(self, pos):
        # on board
        on_board = (0 <= pos[0] < len(self.map) and 0 <= pos[1] < len(self.map[0]))
        if not on_board:
            return False

        # free cell
        value_in_pos = self.map[pos[0]][pos[1]]
        free_cell = (value_in_pos not in [-1, 1, 2])
        return free_cell

    def check_move(self, pos):
        if not self.pos_feasible_on_board(pos):
            return False

        prev_player_position = self.get_player_position_by_current(current=True)
        if not any(utils.tup_add(prev_player_position, move) == pos for move in self.directions):
            # print('moved from', prev_player_position, 'to', pos)
            return False

        return True

    def print_board_to_terminal(self, player_id):
        board_to_print = np.flipud(self.get_map_for_player_i(player_id))
        print('_' * len(board_to_print[0]) * 4)
        for row in board_to_print:
            row = [str(int(x)) if x != -1 else 'X' for x in row]
            print(' | '.join(row))
            print('_' * len(row) * 4)

    def get_map_for_player_i(self, player_id):
        map_copy = self.map.copy()

        pos_player_id = self.get_player_position(player_id)
        pos_second = self.get_player_position(1 - player_id)

        # flip positions
        map_copy[pos_player_id[0]][pos_player_id[1]] = 1
        map_copy[pos_second[0]][pos_second[1]] = 2
        return map_copy

    def get_players_scores(self):
        return self.players_score

    def penalize_player(self, player_id, penalty):
        self.players_score[player_id] -= penalty

    def get_starting_state(self):
        return self.board_patch + sum(self.map_patches, []) + self.players

    def get_dust_on_board(self):
        """ Returns a dictionary of pos:val
            for each dust on the game board (current state)
        """
        dust_pos_val = {pos: fruit_params['value'] for (pos, fruit_params)
                        in self.dust_on_board.items()}

        return dust_pos_val

    def get_player_position(self, player_id):
        pos = np.where(self.map == player_id + 1)
        pos = tuple([ax[0] for ax in pos])
        return pos

    def get_player_position_by_current(self, current=True):
        player_id = self.turn
        if not current:
            player_id = 1 - self.turn

        return tuple(reversed(self.players_positions[player_id]))



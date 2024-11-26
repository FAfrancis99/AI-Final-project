from players.AbstractPlayer import AbstractPlayer
import numpy as np
import os, sys

class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time, penalty_score) # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.board = None             # and add more fields to Player
        self.pos = None
        # map pressed key to direction on board
        self.keys_directions = {'a': self.directions[-1], 
                                'w': self.directions[0], 
                                'd': self.directions[1], 
                                's': self.directions[2]}
        self.cleaned_cells = 0


    def set_game_params(self, board):
        self.board = board
        pos = np.where(board == 1)
        # convert pos to tuple of ints
        self.pos = tuple(ax[0] for ax in pos)


    def set_rival_move(self, pos):
        self.board[pos] = -1


    def is_direction_legal(self, direction):
        i, j = np.add(self.pos, direction)
        if ( 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) 
            and (self.board[i][j] not in [-1, 1, 2]) ):   # then move is legal
            return True
        return False

    def make_move(self, time_limit, players_score):
        assert self.pos is not None
        print('Insert your move:')
        
        direction = None

        direction_legal = False
        while not direction_legal:
            sys.stdout = open(os.devnull, 'w')
            pressed_key = input()
            direction = self.keys_directions[pressed_key]
            direction_legal = self.is_direction_legal(direction)
            sys.stdout = sys.__stdout__
        
        # direction is legal
        self.board[self.pos] = -1 # update prev pos
        self.pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
        self.board[self.pos] = 1 # update cur pos
        self.cleaned_cells += 1

        return direction

    def get_cleaned_cells(self):
        return self.cleaned_cells

    def update_dirt(self, fruits_on_board_dict):
        pass
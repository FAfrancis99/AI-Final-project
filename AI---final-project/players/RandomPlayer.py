import random
from numpy import copy
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
from copy_copy import copy, deepcopy
import networkx as nx
import time
from players.MinimaxPlayer import State

class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,penalty_score)
        self.position = None
        self.opponent_position = None
        self.board = None
        self.dirt_imgs = None
        self.time_limit = None
        self.depth_limit = None
        self.cleaned_cells = 0


    def set_game_params(self, board):
        """

        Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, a 2D matrix of the board.
        No output is expected.
        """
        self.board = copy(board)
        num1 = 0
        num2 = 0
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 1:
                    self.position = (i, j)
                    num1 += 1
                if board[i][j] == 2:
                    self.opponent_position = (i, j)
                    num2 += 1
        assert num1 == 1 and num2 == 1

    def get_algorithm_instance(self):
        return None

    def has_time(self, deadline_time, time_of_last_depth):
        return (deadline_time - time.time()) >= time_of_last_depth

    def make_move(self, time_limit, players_score):
        """Make a random move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifying the Player's movement, chosen from self.directions
        """
        # Calculate the deadline time based on the time limit
        deadline_time = time_limit + time.time() - 0.1
        # Create the current state object
        current_state = State(self.position, self.opponent_position, self.board, self.dirt_imgs, 1, self.penalty_score,
                              players_score, deadline_time, 0)
        # Get all legal moves for the current player
        steps = list(current_state.get_legal_moves(1))
        # If no legal moves, return None (game over or no valid moves)
        if not steps:
            return None
        # Randomly select one of the available moves
        current_move = random.choice(steps)
        # Apply the selected move to get the next state
        next_state = current_state.apply_move_state(1, current_move)
        # Update the player's board and position
        self.board = copy(next_state.board)  # deepcopy
        self.position = copy(next_state.position)
        # Return the chosen move
        self.cleaned_cells += 1

        return current_move

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        self.board[self.opponent_position] = -1
        self.opponent_position = tuple(pos)
        self.board[self.opponent_position] = 2

    def update_dirt(self, dirt_on_board_dict):
        """Update your info on the current dirt on board (if needed).
        input:
            - dirt_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the dirt's position on board,
                                    'value' is the value of this dirt.
        No output is expected.
        """
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] > 2:
                    self.board[i][j] = 0
        for key in dirt_on_board_dict.keys():
            self.board[key] = dirt_on_board_dict[key]
        self.dirt_imgs = copy(dirt_on_board_dict)


    def get_cleaned_cells(self):
        return self.cleaned_cells
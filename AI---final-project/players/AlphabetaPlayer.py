"""
MiniMax Player with AlphaBeta pruning
"""
from players.AbstractPlayer import AbstractPlayer
from players.MinimaxPlayer import State
import SearchAlgos
from copy_copy import copy, deepcopy
import time


def get_algorithm_instance():
    alphabeta = SearchAlgos.AlphaBeta(utility, successor_states, perform_move)
    return alphabeta


def has_time(deadline_time, time_of_last_depth):
    return (deadline_time - time.time()) >= time_of_last_depth


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,
                                penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.position = None
        self.opponent_position = None
        self.board = None
        self.dust = None
        self.time_limit = None
        self.depth_limit = None
        self.cleaned_cells = 0

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
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

    def make_move(self, time_limit, players_score):
        test_time = time.time()
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        deadline_time = time_limit + time.time() - 0.1

        alphabeta_algo = get_algorithm_instance()
        current_state = State(self.position, self.opponent_position, self.board, self.dust, 1, self.penalty_score,
                              players_score, deadline_time, 0)
        steps = current_state.get_legal_moves(1)
        current_move=None
        depth = 0
        time_of_last_depth = 0
        full_tree = False
        while has_time(deadline_time, time_of_last_depth) and depth < current_state.white_squares_num() \
                and not full_tree:
            time_before = time.time()
            current_val, full_tree, current_move = alphabeta_algo.search(current_state, depth, current_state.player)
            depth += 1
            time_after = time.time()
            time_of_last_depth = time_after - time_before

        if current_move is None:
            next_state = current_state.apply_move_state(1, steps)
            self.board = deepcopy(next_state.board)
            self.position = copy(next_state.position)

        next_state = current_state.apply_move_state(1, current_move)
        self.board = deepcopy(next_state.board)
        self.position = copy(next_state.position)
        #print("move time:")
        #print(time.time() - test_time)
        self.cleaned_cells += 1
        return current_move

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        self.board[self.opponent_position] = -1
        self.opponent_position = pos
        self.board[self.opponent_position] = 2

    def update_dirt(self, dust_on_board_dict):
        """Update your info on the current dust on board (if needed).
        input:
            - dust_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the dust's position on board,
                                    'value' is the value of this dust.
        No output is expected.
        """
        # use 'pass' instead of the following line.
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] > 2:
                    self.board[i][j] = 0
        for key in dust_on_board_dict.keys():
            self.board[key] = dust_on_board_dict[key]
        self.dust = copy(dust_on_board_dict)

    def get_cleaned_cells(self):
        return self.cleaned_cells


def successor_states(state, player):
    moves = []
    for move in state.get_legal_moves(player):
        moves.append(move)
    if len(moves)==0:
        return None
    return moves


def utility(state):
    heu = state.heuristic_val()
    return heu


def perform_move(state, player, move):
    return state.apply_move_state(player, move)

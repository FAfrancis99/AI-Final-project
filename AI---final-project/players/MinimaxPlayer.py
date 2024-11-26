from numpy import copy
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
from copy_copy import copy, deepcopy
import networkx as nx
import time

MAX_PATH = 400
BONOS = 20
import numpy as np

def other_player(player):
    return 3 - player

class State:
    def __init__(self, pos, opponent_pos, board, dirt, player, penalty_score, current_score, time, turns):
        self.player = copy(player)
        self.position = tuple(copy(pos))
        self.opponent_position = tuple(copy(opponent_pos))
        self.board = deepcopy(board)  # Use custom_deepcopy instead of deepcopy
        self.dirt = deepcopy(dirt)  # Use custom_deepcopy instead of deepcopy
        self.penalty = penalty_score
        self.score = copy(current_score)
        self.time_limit = time
        self.num_of_turns = copy(turns)
        # self.cleaned_cells = 0

    def get_player_position(self, player):
        if player == 1:
            return self.position
        if player == 2:
            return self.opponent_position

    def apply_move_state(self, player: int, move: (int, int)):
        assert move in self.get_legal_moves(player)
        old_position = self.get_player_position(player)
        new_position = (old_position[0] + move[0]), (old_position[1] + move[1])
        new_score = self.score
        if new_position in self.dirt:
            new_score[player - 1] = self.score[player - 1] + self.dirt[new_position]
        new_board = deepcopy(self.board)  # Use custom_deepcopy instead of copy
        new_board[new_position] = player
        new_board[old_position] = -1
        # self.cleaned_cells += 1
        if player == 1:
            new_state = State(new_position, self.opponent_position, new_board, self.dirt, player, self.penalty,
                              new_score, self.time_limit, self.num_of_turns)
        else:
            new_state = State(self.position, new_position, new_board, self.dirt, player, self.penalty,
                              new_score, self.time_limit, self.num_of_turns)
        new_state.num_of_turns += 1
        return new_state

    def build_current_graph(self):
        graph = nx.Graph()
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                graph.add_node((i, j))
                if self.board[i][j] != -1:
                    if i < len(self.board) - 1 and (self.board[i + 1][j] > 2 or self.board[i + 1][j] == 0):
                        graph.add_edge((i, j), (i + 1, j))
                    if i > 0 and (self.board[i - 1][j] > 2 or self.board[i - 1][j] == 0):
                        graph.add_edge((i, j), (i - 1, j))
                    if j < len(self.board[i]) - 1 and (self.board[i][j + 1] > 2 or self.board[i][j + 1] == 0):
                        graph.add_edge((i, j), (i, j + 1))
                    if j > 0 and (self.board[i][j - 1] > 2 or self.board[i][j - 1] == 0):
                        graph.add_edge((i, j), (i, j - 1))
        return graph

    def achievable_squares_score(self, graph):
        # print(graph.nodes())
        if isinstance(self.position, np.ndarray):
            self.position = tuple(self.position)
        my_achievables = len(nx.shortest_path(graph, source=self.position))
        return my_achievables

    def shortest_path_to_best_dirt_score(self, graph):
        sum = 0
        if self.dirt is None:
            return 1
        for location in self.dirt:
            if nx.has_path(graph, self.position, location):
                path = nx.shortest_path_length(graph, source=self.position, target=location)
                if path == 0 and self.dirt[location]:
                    sum += self.dirt[location]
                else:
                    sum += self.dirt[location] / path
        return sum

    def path_between_players_score(self, graph):
        if nx.has_path(graph, self.position, self.opponent_position):
            return BONOS
        else:
            return -BONOS

    def get_player_loc(self, player):
        if player == 1:
            return self.position
        elif player == 2:
            return self.opponent_position

    def get_legal_moves(state, player: int):  # returns the direction!
        loc = state.get_player_loc(player)
        for dir in {(0, 1), (1, 0), (0, -1), (-1, 0)}:
            i = loc[0] + dir[0]
            j = loc[1] + dir[1]
            if 0 <= i < len(state.board) and 0 <= j < len(state.board[0]) and (
                    state.board[i][j] == 0 or state.board[i][j] > 2):  # then move is legal
                yield dir

    def num_of_legal_moves(self, player):
        num = 0
        for direction in self.get_legal_moves(player):
            num += 1
        return num

    def min_steps_score(self):
        return (4 - self.num_of_legal_moves(1)) * 10

    def max_squares_on_my_side_score(self):
        my_side_left_right = 0
        my_side_up_down = 0

        if self.position[1] <= self.opponent_position[1]:
            my_side_left_right = self.position[1]
        else:
            my_side_left_right = len(self.board[0]) - self.position[1]

        if self.position[0] <= self.opponent_position[0]:
            my_side_up_down = self.position[0]
        else:
            my_side_up_down = len(self.board[0]) - self.position[0]

        return my_side_left_right + my_side_up_down

    def is_hole_score(self):
        if self.num_of_legal_moves(1) == 0:
            return -self.penalty
        else:
            return 0

    def heuristic_val(self) -> float:
        hole = self.is_hole_score()
        my_side = self.max_squares_on_my_side_score()
        steps_score = self.min_steps_score()
        graph = self.build_current_graph()
        achievables = self.achievable_squares_score(graph)
        path_between_players = self.path_between_players_score(graph)
        shortest_to_dirt = self.shortest_path_to_best_dirt_score(graph)
        heuristic_val = hole + my_side + shortest_to_dirt + path_between_players + achievables + steps_score
        heuristic_val += self.score[0] - self.score[1]
        return heuristic_val

    def get_winning_move(self, player: int) -> (int, int):
        assert self.num_of_legal_moves(player) > 0
        winning_move = None
        for move in self.get_legal_moves(player):
            new_state = self.apply_move_state(player, move)
            if self.num_of_legal_moves(new_state, player) > 0:
                winning_move = move
        return winning_move

    def white_squares_num(self):
        num = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == 0 or self.board[i][j] > 2:
                    num +=1
        return num



class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
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
        min_max = SearchAlgos.MiniMax(utility, successor_states, perform_move)
        return min_max

    def has_time(self, deadline_time, time_of_last_depth):
        return (deadline_time - time.time()) >= time_of_last_depth

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        minimax_algo = self.get_algorithm_instance()
        deadline_time = time_limit + time.time() - 0.1
        current_state = State(self.position, self.opponent_position, self.board, self.dirt_imgs, 1, self.penalty_score,
                              players_score, deadline_time, 0)
        steps = current_state.get_legal_moves(1)
        current_move=None
        depth = 0
        time_of_last_depth = 0
        full_tree = False
        while self.has_time(deadline_time, time_of_last_depth) and depth < current_state.white_squares_num() \
            and not full_tree:
            time_before = time.time()
            current_val, full_tree, times_up, current_move = minimax_algo.search(current_state, depth, current_state.player)
            depth += 1
            time_after = time.time()
            time_of_last_depth = time_after - time_before

        if current_move is None:
            next_state = current_state.apply_move_state(1, steps)
            self.board = copy(next_state.board) #deepcopy
            self.position = copy(next_state.position)

        next_state = current_state.apply_move_state(1, current_move)
        self.board = copy(next_state.board) #deepcopy
        self.position = copy(next_state.position)
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

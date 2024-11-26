"""Search Algos: MiniMax, AlphaBeta
"""

from utils import ALPHA_VALUE_INIT, BETA_VALUE_INIT
import time
import math
import random




class SearchAlgos:
    def __init__(self, utility, succ, perform_move, goal=None):
        """The constructor for all the search algos.
        You can code these functions as you like to, 
        and use them in MiniMax and AlphaBeta algos as learned in class
        :param utility: The utility function.
        :param succ: The succesor function.
        :param perform_move: The perform move function.
        :param goal: function that check if you are in a goal state.
        """
        self.utility = utility
        self.succ = succ
        self.perform_move = perform_move

    def search(self, state, depth, maximizing_player):
        pass


class MiniMax(SearchAlgos):

    def search(self, state, depth, maximizing_player) -> (int, bool, bool, (int, int)):
        """Start the MiniMax algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        steps = self.succ(state, maximizing_player)
        times_up = time.time() >= state.time_limit
        if times_up is True:
            if steps is None:
                return int(self.utility(state)), False, True, None
            new_state = state.apply_move_state(maximizing_player, steps[0])
            return int(self.utility(new_state)), False, True, steps[0]
        reached_the_leaves = 0
        if steps is None or not steps:
            state.score[maximizing_player - 1] = state.score[maximizing_player - 1] - state.penalty
            return state.score[0] - state.score[1]+self.utility(state), True, False, None
        if depth == 0:
            new_state = state.apply_move_state(maximizing_player, steps[0])
            return int(self.utility(new_state)), False, False, steps[0]

        elif maximizing_player == 1:  # our turn
            max_min = -math.inf
            best_move = None
            for move in steps:
                new_state = state.apply_move_state(maximizing_player, move)
                current_val, full_tree, times_up, current_move = self.search(new_state, depth - 1,
                3 - maximizing_player)
                if current_val > max_min:
                    max_min = current_val
                    best_move = move
                if full_tree is True:
                    reached_the_leaves += 1

                if times_up is True:
                    return max_min, reached_the_leaves == state.num_of_legal_moves(
                        maximizing_player), times_up, best_move


        elif maximizing_player == 2:  # opponent turn
            max_min = math.inf
            best_move = None
            for move in steps:
                new_state = state.apply_move_state(maximizing_player, move)
                current_val, full_tree, times_up, current_move = self.search(new_state, depth - 1,
                                                                             3 - maximizing_player)
                if current_val < max_min:
                    max_min = current_val
                    best_move = move
                if full_tree is True:
                    reached_the_leaves += 1

                if times_up is True:
                    return max_min, reached_the_leaves == state.num_of_legal_moves(
                            maximizing_player), times_up, best_move

        times_up = time.time() == state.time_limit
        return max_min, reached_the_leaves == state.num_of_legal_moves(maximizing_player), times_up,  best_move


class AlphaBeta(SearchAlgos):

    def search(self, state, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
        """Start the AlphaBeta algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :param alpha: alpha value
        :param: beta: beta value
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        reached_the_leaves = 0
        steps = self.succ(state, maximizing_player)
        if steps is None or not steps:
            state.score[maximizing_player - 1] = state.score[maximizing_player - 1] - state.penalty
            return state.score[0] - state.score[1], True, None
        if depth == 0:
            #new_state = state.apply_move_state(maximizing_player, steps[0])
            return int(self.utility(state)), False, None

        elif maximizing_player == 1:  # our turn
            max_min = -math.inf
            best_move = None
            for move in steps:
                new_state = state.apply_move_state(maximizing_player, move)
                current_val, full_tree, current_move = self.search(new_state, depth - 1, 3 - maximizing_player, alpha, beta)
                if current_val > max_min:
                    max_min = current_val
                    best_move = move
                if full_tree is True:
                    reached_the_leaves += 1
                alpha = max(alpha, max_min)
                if beta <= max_min:
                    return math.inf, True, None

        elif maximizing_player == 2:  # opponent turn
            max_min = math.inf
            best_move = None
            for move in steps:
                new_state = state.apply_move_state(maximizing_player, move)
                current_val, full_tree, current_move = self.search(new_state, depth - 1, 3 - maximizing_player, alpha, beta)
                if current_val < max_min:
                    max_min = current_val
                    best_move = move
                if full_tree is True:
                    reached_the_leaves += 1
                beta = min(beta, max_min)
                if alpha >= max_min:
                    return -math.inf, True, None

        return max_min, reached_the_leaves == state.num_of_legal_moves(maximizing_player), best_move


class QLearning:
    def __init__(self, learning_rate=0.2, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.99, min_exploration_rate=0.1, n_step=1):
        self.q_table = {}  # Dictionary to store Q-values
        self.learning_rate = learning_rate  # Alpha
        self.discount_factor = discount_factor  # Gamma
        self.exploration_rate = exploration_rate  # Epsilon
        self.exploration_decay = exploration_decay  # Epsilon decay
        self.min_exploration_rate = min_exploration_rate  # Minimum epsilon
        self.n_step = n_step  # N-step learning for faster convergence

    def get_state(self, state):
        """Convert the game state to a hashable format (tuple or string) to store in the Q-table."""
        return tuple(state.position + state.opponent_position + tuple(state.board.flatten()))

    def choose_action(self, state, legal_moves):
        """Choose an action based on the current state using the epsilon-greedy strategy."""
        state_key = self.get_state(state)

        # Exploration vs Exploitation
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(legal_moves)  # Explore: choose random action
        else:
            # Exploit: choose the action with the max Q-value
            q_values = [self.q_table.get((state_key, action), 0) for action in legal_moves]
            max_q_value = max(q_values)
            max_actions = [action for action, q_value in zip(legal_moves, q_values) if q_value == max_q_value]
            return random.choice(max_actions)

    def update_q_value(self, current_state, action, reward, next_state, legal_moves, terminal_state=False):
        """Update the Q-value for the given state-action pair using the Q-learning update rule."""
        state_key = self.get_state(current_state)
        next_state_key = self.get_state(next_state)

        # Get the current Q-value (default to 0 if not in Q-table)
        current_q = self.q_table.get((state_key, action), 0)

        # Get the maximum Q-value for the next state
        future_q = 0 if terminal_state else max([self.q_table.get((next_state_key, next_action), 0) for next_action in legal_moves], default=0)

        # Q-learning formula with n-step adjustment
        new_q = current_q + self.learning_rate * (reward + (self.discount_factor ** self.n_step) * future_q - current_q)

        # Update the Q-table
        self.q_table[(state_key, action)] = new_q

    def update_q_value_n_step(self, rewards, states, actions, legal_moves):
        """N-step Q-learning update for faster convergence."""
        G = 0
        for t in reversed(range(len(rewards))):
            G = self.discount_factor * G + rewards[t]
            if t + self.n_step < len(states):
                state_key = self.get_state(states[t])
                next_state_key = self.get_state(states[t + self.n_step])
                future_q = max([self.q_table.get((next_state_key, next_action), 0) for next_action in legal_moves], default=0)
                G += (self.discount_factor ** self.n_step) * future_q
            action = actions[t]
            self.q_table[(self.get_state(states[t]), action)] = self.q_table.get((self.get_state(states[t]), action), 0) + self.learning_rate * (G - self.q_table.get((self.get_state(states[t]), action), 0))

    def decay_exploration_rate(self):
        """Decay the exploration rate to balance exploration and exploitation."""
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)



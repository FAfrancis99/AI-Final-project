
import time
import random
from players.AbstractPlayer import AbstractPlayer
from players.MinimaxPlayer import State
import SearchAlgos

class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score, learning_rate=0.2, discount_factor=0.5, exploration_rate= 0.5,
                 exploration_decay=0.1, min_exploration_rate=0.2, n_step=5, base_move_time=0.1):
        AbstractPlayer.__init__(self, game_time, penalty_score)
        self.q_table = {}  # Dictionary to store Q-values
        self.learning_rate = learning_rate  # Alpha
        self.discount_factor = discount_factor  # Gamma
        self.exploration_rate = exploration_rate  # Epsilon
        self.exploration_decay = exploration_decay  # Epsilon decay
        self.min_exploration_rate = min_exploration_rate  # Minimum epsilon
        self.n_step = n_step  # N-step for lookahead
        self.base_move_time = base_move_time  # Base time for making a move (non-fixed)
        self.qLearning = SearchAlgos.QLearning()
        self.cleaned_cells = 0

    def set_game_params(self, board):
        """Set the game parameters needed for this player."""
        self.board = board
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 1:
                    self.position = (i, j)
                if board[i][j] == 2:
                    self.opponent_position = (i, j)

    def make_move(self, time_limit, players_score):
        """Make a move using N-step Q-Learning with adaptive computation time."""
        start_time = time.time()

        current_state = State(self.position, self.opponent_position, self.board, self.dirt_imgs, 1, self.penalty_score,
                              players_score, time_limit, 0)
        legal_moves = list(current_state.get_legal_moves(1))

        # Check for safe moves that don't result in being surrounded by gray cells
        safe_moves = [move for move in legal_moves if not self.is_surrounded_by_gray(self.get_next_position(move))]
        if not safe_moves:
            safe_moves = legal_moves

        # N-step lookahead for each legal move
        best_move = None
        max_cumulative_reward = float('-inf')

        for move in safe_moves:
            cumulative_reward, _ = self.simulate_n_steps(current_state, move, self.n_step, 0)
            if cumulative_reward > max_cumulative_reward:
                max_cumulative_reward = cumulative_reward
                best_move = move

        chosen_move = best_move

        # Apply the chosen move
        next_state = current_state.apply_move_state(1, chosen_move)
        reward = self.calculate_reward(current_state, next_state)
        self.qLearning.update_q_value(current_state, chosen_move, reward, next_state,
                                      list(next_state.get_legal_moves(1)))
        self.qLearning.decay_exploration_rate()

        self.board = next_state.board
        self.position = next_state.position
        self.cleaned_cells += 1

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Add an adaptive random delay to slow down fast decisions but not too much
        # Add an adaptive random delay to slow down fast decisions but not too much
        if elapsed_time < self.base_move_time:
            # Random delay between 0 and a fraction of base_move_time (e.g., 50% - 150% of base_move_time)
            random_delay = random.uniform(0.5 * self.base_move_time, 1.5 * self.base_move_time)
            time.sleep(max(0, random_delay - elapsed_time))  # Ensure non-negative sleep time

        return chosen_move

    def simulate_n_steps(self, state, move, steps_remaining, cumulative_reward):
        """Recursively simulate N steps and calculate cumulative reward."""
        if steps_remaining == 0:
            return cumulative_reward, state

        # Apply the move
        next_state = state.apply_move_state(1, move)
        reward = self.calculate_reward(state, next_state)
        cumulative_reward += reward

        # Get the legal moves in the new state
        legal_moves = list(next_state.get_legal_moves(1))

        if not legal_moves or steps_remaining == 1:
            return cumulative_reward, next_state

        # Recursively simulate the next steps
        max_future_reward = float('-inf')
        for future_move in legal_moves:
            future_cumulative_reward, _ = self.simulate_n_steps(next_state, future_move, steps_remaining - 1, cumulative_reward)
            if future_cumulative_reward > max_future_reward:
                max_future_reward = future_cumulative_reward

        return max_future_reward, next_state

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival."""
        self.board[self.opponent_position] = -1  # Clear the previous opponent's position
        self.opponent_position = tuple(pos)
        self.board[self.opponent_position] = 2

    def update_dirt(self, dirt_on_board_dict):
        """Update your info on the current dirt on the board."""
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] > 2:
                    self.board[i][j] = 0  # Clear old dirt
        for key in dirt_on_board_dict.keys():
            self.board[key] = dirt_on_board_dict[key]  # Place new dirt
        self.dirt_imgs = dirt_on_board_dict

    def calculate_reward(self, current_state, next_state):
        """Calculate the reward based on the state transition."""
        reward = 0
        if next_state.position in self.dirt_imgs:
            reward += self.dirt_imgs[next_state.position]  # Reward for collecting dirt
        if next_state.position == current_state.position:
            reward -= 10  # Penalty for staying in the same position
        if self.is_surrounded_by_gray(next_state.position):
            reward -= self.penalty_score  # Penalty for being surrounded by gray cells
        return reward

    def is_surrounded_by_gray(self, position):
        """Check if the given position is surrounded by gray cells."""
        x, y = position
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.board) and 0 <= ny < len(self.board[0]) and self.board[nx][ny] != -1:
                return False
        return True

    def get_next_position(self, move):
        """Calculate the next position based on the move."""
        x, y = self.position
        dx, dy = move
        return (x + dx, y + dy)

    def get_cleaned_cells(self):
        """Return the number of cleaned cells."""
        return self.cleaned_cells

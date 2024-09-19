"""
minimax_agent.py
author: Nur Ahmed (optimized version)
"""
import agent
import game
import time
import random

class MinimaxAgent(agent.Agent):
    def __init__(self, initial_state: game.GameState, piece: str):
        super().__init__(initial_state, piece)
        self.transposition_table = {}  # Cache for evaluated positions

    def introduce(self):
        """
        returns a multi-line introduction string
        :return: intro string
        """
        return ("My name is Minimax Agent.\n" +
                "I was created by Nur Ahmed.\n" +
                "I'm ready to play K-in-a-Row!")

    def nickname(self):
        """
        returns a short nickname for the agent
        :return: nickname
        """
        return "Mini"

    def choose_move(self, state: game.GameState, time_limit: float) -> (int, int):
        """
        Selects a move to make on the given game board. Returns a move
        :param state: current game state
        :param time_limit: time (in seconds) before you'll be cutoff and forfeit the game
        :return: move (x,y)
        """
        start_time = time.time()
        best_move = None
        depth = 1

        while time.time() - start_time < time_limit * 0.95:  # Use 95% of the time limit
            move, _ = self.minimax(state, depth, start_time, time_limit)
            if move is not None:
                best_move = move
            else:
                break
            depth += 1

        return best_move if best_move else self.get_random_move(state)

    def minimax(self, state: game.GameState, depth_remaining: int, start_time: float, time_limit: float,
                alpha: float = float('-inf'), beta: float = float('inf')) -> ((int, int), float):
        """
        Uses minimax to evaluate the given state and choose the best action from this state. Uses the next_player of the
        given state to decide between min and max. Recursively calls itself to reach depth_remaining layers. Optionally
        uses alpha, beta for pruning, and/or z_hashing for zobrist hashing.
        :param state: State to evaluate
        :param depth_remaining: number of layers left to evaluate
        :param start_time: start time of the search
        :param time_limit: time limit for the search
        :param alpha: alpha value for pruning
        :param beta: beta value for pruning
        :return: move (x,y) or None, state evaluation
        """
        if time.time() - start_time > time_limit * 0.95:
            return None, self.static_eval(state)

        if depth_remaining == 0 or state.winner() is not None:
            return None, self.static_eval(state)

        state_hash = self.hash_state(state)
        if state_hash in self.transposition_table and self.transposition_table[state_hash][0] >= depth_remaining:
            return self.transposition_table[state_hash][1], self.transposition_table[state_hash][2]

        is_maximizing = state.next_player == self.piece
        best_move = None
        best_score = float('-inf') if is_maximizing else float('inf')

        for move in self.get_ordered_moves(state):
            new_state = state.make_move(move)
            _, score = self.minimax(new_state, depth_remaining - 1, start_time, time_limit, alpha, beta)
            
            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, best_score)
            
            if beta <= alpha:
                break

        self.transposition_table[state_hash] = (depth_remaining, best_move, best_score)
        return best_move, best_score

    def static_eval(self, state: game.GameState) -> float:
        """
        Evaluates the given state. States good for X should be larger that states good for O.
        :param state: state to evaluate
        :return: evaluation of the state
        """
        score = 0
        for row in state.board:
            score += self.evaluate_line(row, self.piece, state.k)
        for col in zip(*state.board):
            score += self.evaluate_line(col, self.piece, state.k)
        return score

    def evaluate_line(self, line: list[str], agent_piece: str, k: int) -> float:
        """
        Evaluates a single line (row, column, or diagonal) for potential wins
        :param line: list of pieces in the line
        :param agent_piece: the piece of the current agent
        :param k: number of pieces in a row needed to win
        :return: score for the line
        """
        score = 0
        opponent_piece = game.O_PIECE if agent_piece == game.X_PIECE else game.X_PIECE
        
        for i in range(len(line) - k + 1):
            segment = line[i:i+k]
            if game.BLOCK_PIECE not in segment:
                agent_count = segment.count(agent_piece)
                opponent_count = segment.count(opponent_piece)
                
                if opponent_count == 0:
                    score += 10 ** agent_count
                elif agent_count == 0:
                    score -= 10 ** opponent_count

        return score

    def get_ordered_moves(self, state: game.GameState) -> list[(int, int)]:
        """
        Returns a list of possible moves, potentially ordered for better pruning
        :param state: current game state
        :return: list of possible moves as (x, y) tuples
        """
        moves = [(x, y) for x in range(state.w) for y in range(state.h) if state.is_valid_move((x, y))]
        # Simple move ordering: prefer center moves
        center_x, center_y = state.w // 2, state.h // 2
        moves.sort(key=lambda move: abs(move[0] - center_x) + abs(move[1] - center_y))
        return moves

    def get_random_move(self, state: game.GameState) -> (int, int):
        """
        Selects a random valid move from the game state
        :param state: current game state
        :return: a random valid move as (x, y) tuple
        """
        valid_moves = [(x, y) for x in range(state.w) for y in range(state.h) if state.is_valid_move((x, y))]
        return random.choice(valid_moves) if valid_moves else (0, 0)

    def hash_state(self, state: game.GameState) -> int:
        """
        Creates a hash of the current game state for the transposition table
        :param state: current game state
        :return: hash value of the state
        """
        return hash(tuple(tuple(row) for row in state.board) + (state.next_player,))
"""
minimax_agent.py
author: Nur Ahmed (optimized version)
"""
import agent
import game
import time
import random

# Define game constants if not already defined in the game module
EMPTY = game.EMPTY if hasattr(game, 'EMPTY') else '.'
X_PIECE = game.X_PIECE if hasattr(game, 'X_PIECE') else 'X'
O_PIECE = game.O_PIECE if hasattr(game, 'O_PIECE') else 'O'
BLOCK_PIECE = game.BLOCK_PIECE if hasattr(game, 'BLOCK_PIECE') else '#'

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
            move, _ = self.minimax(state, depth, float('-inf'), float('inf'), True, start_time, time_limit)
            if move is not None:
                best_move = move
            else:
                break
            depth += 1

        return best_move if best_move else self.get_random_move(state)

    def minimax(self, state: game.GameState, depth: int, alpha: float, beta: float, maximizing_player: bool, start_time: float, time_limit: float) -> ((int, int), float):
        """
        Uses minimax to evaluate the given state and choose the best action from this state. Uses the next_player of the
        given state to decide between min and max. Recursively calls itself to reach depth_remaining layers. Optionally
        uses alpha, beta for pruning, and/or z_hashing for zobrist hashing.
        :param state: State to evaluate
        :param depth: current search depth
        :param alpha: alpha value for pruning
        :param beta: beta value for pruning
        :param maximizing_player: True if maximizing, False if minimizing
        :param start_time: start time of the search
        :param time_limit: time limit for the search
        :return: move (x,y) or None, state evaluation
        """
        if time.time() - start_time > time_limit * 0.95:
            return None, self.static_eval(state)

        if depth == 0 or state.winner() is not None:
            return None, self.quiescence_search(state, alpha, beta, maximizing_player, start_time, time_limit)

        state_hash = self.hash_state(state)
        if state_hash in self.transposition_table and self.transposition_table[state_hash][0] >= depth:
            return self.transposition_table[state_hash][1], self.transposition_table[state_hash][2]

        is_maximizing = state.next_player == self.piece
        best_move = None
        best_score = float('-inf') if is_maximizing else float('inf')

        for move in self.get_ordered_moves(state):
            new_state = state.make_move(move)
            _, score = self.minimax(new_state, depth - 1, alpha, beta, not is_maximizing, start_time, time_limit)
            
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

        self.transposition_table[state_hash] = (depth, best_move, best_score)
        return best_move, best_score

    def static_eval(self, state: game.GameState) -> float:
        """
        Evaluates the given state
        :param state: State to evaluate
        :return: state evaluation
        """
        score = 0
        for row in range(state.h):
            score += self.evaluate_line([state.board[row][col] for col in range(state.w)], self.piece, state.k)
        for col in range(state.w):
            score += self.evaluate_line([state.board[row][col] for row in range(state.h)], self.piece, state.k)
        
        # Add diagonal evaluations
        for i in range(state.h - state.k + 1):
            for j in range(state.w - state.k + 1):
                score += self.evaluate_line([state.board[i+x][j+x] for x in range(state.k)], self.piece, state.k)
                score += self.evaluate_line([state.board[i+x][j+state.k-1-x] for x in range(state.k)], self.piece, state.k)

        return score

    def evaluate_line(self, line: list[str], agent_piece: str, k: int) -> float:
        """
        Evaluates a line of the board
        :param line: list of pieces in the line
        :param agent_piece: the agent's piece
        :param k: number of pieces in a row needed to win
        :return: evaluation score for the line
        """
        score = 0
        opponent_piece = O_PIECE if agent_piece == X_PIECE else X_PIECE
        
        for i in range(len(line) - k + 1):
            segment = line[i:i+k]
            if BLOCK_PIECE not in segment:
                agent_count = segment.count(agent_piece)
                opponent_count = segment.count(opponent_piece)
                empty_count = segment.count(EMPTY)
                
                if opponent_count == 0:
                    if agent_count == k:
                        score += 1000000  # Win condition
                    else:
                        score += 10 ** agent_count
                elif agent_count == 0:
                    if opponent_count == k:
                        score -= 1000000  # Loss condition
                    else:
                        score -= 10 ** opponent_count
                
                # Favor positions that allow for future wins
                score += empty_count * 0.1

        return score

    def get_ordered_moves(self, state: game.GameState) -> list[(int, int)]:
        """
        Returns a list of possible moves, potentially ordered for better pruning
        :param state: current game state
        :return: list of possible moves as (x, y) tuples
        """
        moves = [(x, y) for x in range(state.w) for y in range(state.h) if state.is_valid_move((x, y))]
        
        # Evaluate each move
        move_scores = []
        for move in moves:
            new_state = state.make_move(move)
            score = self.static_eval(new_state)
            move_scores.append((move, score))
        
        # Sort moves based on their scores, with the best moves first
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [move for move, _ in move_scores]

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

    def quiescence_search(self, state: game.GameState, alpha: float, beta: float, maximizing_player: bool, start_time: float, time_limit: float, depth: int = 0) -> float:
        """
        Quiescence search to avoid horizon effect
        :param state: current game state
        :param alpha: alpha value for pruning
        :param beta: beta value for pruning
        :param maximizing_player: True if maximizing, False if minimizing
        :param start_time: start time of the search
        :param time_limit: time limit for the search
        :param depth: current quiescence search depth
        :return: evaluation score
        """
        if time.time() - start_time > time_limit * 0.95 or depth > 5:  # Limit quiescence search depth
            return self.static_eval(state)

        stand_pat = self.static_eval(state)
        if maximizing_player:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        for move in self.get_ordered_moves(state):
            new_state = state.make_move(move)
            if new_state.winner() is not None:  # Only consider captures or winning moves
                score = self.quiescence_search(new_state, alpha, beta, not maximizing_player, start_time, time_limit, depth + 1)
                if maximizing_player:
                    alpha = max(alpha, score)
                    if alpha >= beta:
                        return beta
                else:
                    beta = min(beta, score)
                    if beta <= alpha:
                        return alpha

        return alpha if maximizing_player else beta
"""
minimax_agent.py
author: Nur Ahmed
"""
import agent
import game
import time

class MinimaxAgent(agent.Agent):
    def __init__(self, initial_state: game.GameState, piece: str):
        super().__init__(initial_state, piece)

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
        best_move = (0,0)
        best_move, _ = self.minimax(state, 3)

        return best_move

    def minimax(self, state: game.GameState, depth_remaining: int, time_limit: float = None,
                alpha: float = None, beta: float = None, z_hashing=None) -> ((int, int), float):
        """
        Uses minimax to evaluate the given state and choose the best action from this state. Uses the next_player of the
        given state to decide between min and max. Recursively calls itself to reach depth_remaining layers. Optionally
        uses alpha, beta for pruning, and/or z_hashing for zobrist hashing.
        :param state: State to evaluate
        :param depth_remaining: number of layers left to evaluate
        :param time_limit: argument for your use to make sure you return before the time limit. None means no time limit
        :param alpha: alpha value for pruning
        :param beta: beta value for pruning
        :param z_hashing: zobrist hashing data
        :return: move (x,y) or None, state evaluation
        """
        if depth_remaining == 0 or state.winner() is not None:
            return None, self.static_eval(state)

        is_maximizing = state.next_player == self.piece
        best_move = None

        if alpha is None:
            alpha = float('-inf')
        if beta is None:
            beta = float('inf')

        if is_maximizing:
            best_score = float('-inf')
            for row in range(state.w):
                for col in range(state.h):
                    if state.is_valid_move((row, col)):
                        new_state = state.make_move((row, col))
                        _, score = self.minimax(new_state, depth_remaining - 1, time_limit, alpha, beta)
                        
                        if score > best_score:
                            best_score = score
                            best_move = (row, col)
                        alpha = max(alpha, score)
                        if beta <= alpha:
                            break
            return best_move, best_score
        else:
            best_score = float('inf')
            for row in range(state.w):
                for col in range(state.h):
                    if state.is_valid_move((row, col)):
                        new_state = state.make_move((row, col))
                        _, score = self.minimax(new_state, depth_remaining - 1, time_limit, alpha, beta)
                        
                        if score < best_score:
                            best_score = score
                            best_move = (row, col)
                        beta = min(beta, score)
                        if beta <= alpha:
                            break
            return best_move, best_score

    def static_eval(self, state: game.GameState) -> float:
        """
        Evaluates the given state. States good for X should be larger that states good for O.
        :param state: state to evaluate
        :return: evaluation of the state
        """
        score = 0
        lines = []

        # Rows and Columns
        for i in range(state.w):
            lines.append(state.board[i])  # Row
            lines.append([state.board[j][i] for j in range(state.h)])  # Column

        # Diagonals - Left-to-Right and Right-to-Left
        for d in range(1 - state.w, state.h):
            # Left-to-Right Diagonals
            lr_diag = [state.board[i][d + i] for i in range(max(0, -d), min(state.w, state.h - d)) if 0 <= d + i < state.h]
            if lr_diag:
                lines.append(lr_diag)

            # Right-to-Left Diagonals
            rl_diag = [state.board[i][state.h - 1 - d - i] for i in range(max(0, -d), min(state.w, state.h - d)) if 0 <= state.h - 1 - d - i < state.h]
            if rl_diag:
                lines.append(rl_diag)

        # Evaluate each line
        for line in lines:
            score += self.evaluate_line(line, self.piece, state.k)

        return score

    def evaluate_line(self, line: list[str], agent_piece: str, k: int) -> float:
        score = 0
        opponent_piece = ''
        # Determines opponent piece by referencing agent piece
        if agent_piece == game.X_PIECE:
            opponent_piece = game.O_PIECE
        else:
            opponent_piece = game.X_PIECE
            
        # Check for potential sequences of length k
        for i in range(len(line) - k + 1):
            segment = line[i:i+k]
            if game.BLOCK_PIECE not in segment:
                agent_count = segment.count(agent_piece)
                opponent_count = segment.count(opponent_piece)
                
                if opponent_count == 0 and agent_count > 0:
                    # Score positively based on the number of agent's pieces in the segment
                    score += agent_count ** 2  # Exponential scoring based on number of pieces
                elif agent_count == 0 and opponent_count > 0:
                    # Score negatively based on the number of opponent's pieces in the segment
                    score -= opponent_count ** 2

        return score

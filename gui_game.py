import customtkinter as ctk
import game
import agent
from minimax_agent import MinimaxAgent
import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class KInARowGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("K-in-a-Row")
        self.master.geometry("600x600")  # Increased height
        self.master.minsize(400, 400)  # Set minimum size
        self.master.configure(bg="light gray")
        self.game_state = None
        self.player_agent = None
        self.ai_agent = None
        self.buttons = []
        self.game_mode = ctk.StringVar(value="human_vs_ai")
        self.ai_type = ctk.StringVar(value="minimax")
        self.board_size = ctk.StringVar(value="3x3")
        self.game_type = ctk.StringVar(value="standard")
        self.info_frame = None
        self.player_info_label = None
        self.turn_label = None
        
        self.create_menu()

        # Create a custom font for X and O
        self.game_font = tkfont.Font(family="Arial", size=36, weight="bold")

    def create_menu(self):
        self.clear_widgets()

        menu_frame = ctk.CTkFrame(self.master)
        menu_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(menu_frame, text="Game Settings", font=("Roboto", 24)).pack(pady=10)

        ctk.CTkLabel(menu_frame, text="Game Mode:").pack(pady=5)
        ctk.CTkRadioButton(menu_frame, text="Human vs AI", variable=self.game_mode, value="human_vs_ai").pack()
        ctk.CTkRadioButton(menu_frame, text="AI vs AI", variable=self.game_mode, value="ai_vs_ai").pack()

        ctk.CTkLabel(menu_frame, text="AI Type:").pack(pady=5)
        ctk.CTkRadioButton(menu_frame, text="MinimaxAgent", variable=self.ai_type, value="minimax").pack()
        ctk.CTkRadioButton(menu_frame, text="Random Agent", variable=self.ai_type, value="random").pack()

        ctk.CTkLabel(menu_frame, text="Board Size:").pack(pady=5)
        ctk.CTkOptionMenu(menu_frame, variable=self.board_size, values=["3x3", "5x5", "7x7"]).pack()

        ctk.CTkLabel(menu_frame, text="Game Type:").pack(pady=5)
        ctk.CTkOptionMenu(menu_frame, variable=self.game_type, values=["standard", "no_corners", "no_corners_small"]).pack()

        ctk.CTkButton(menu_frame, text="Start Game", command=self.start_game).pack(pady=20)

    def create_info_frame(self):
        if self.info_frame:
            self.info_frame.destroy()
        self.info_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.info_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        self.player_info_label = ctk.CTkLabel(self.info_frame, text="")
        self.player_info_label.pack(side="left", padx=10)

        self.turn_label = ctk.CTkLabel(self.info_frame, text="")
        self.turn_label.pack(side="right", padx=10)

    def start_game(self):
        self.game_state = self.create_game_state()
        
        if self.game_mode.get() == "human_vs_ai":
            self.player_agent = None
            if self.ai_type.get() == "minimax":
                self.ai_agent = MinimaxAgent(self.game_state, game.O_PIECE)
            else:
                self.ai_agent = agent.Agent(self.game_state, game.O_PIECE)
        else:  # AI vs AI
            if self.ai_type.get() == "minimax":
                self.player_agent = MinimaxAgent(self.game_state, game.X_PIECE)
                self.ai_agent = agent.Agent(self.game_state, game.O_PIECE)
            else:
                self.player_agent = agent.Agent(self.game_state, game.X_PIECE)
                self.ai_agent = MinimaxAgent(self.game_state, game.O_PIECE)

        self.create_board()
        self.create_info_frame()
        self.update_info_label()

        if self.game_mode.get() == "ai_vs_ai":
            self.master.after(1000, self.make_ai_move)

    def create_game_state(self):
        game_type = self.game_type.get()
        board_size = tuple(map(int, self.board_size.get().split('x')))

        if game_type == "standard":
            k = min(board_size)
            return game.GameState.empty(board_size, k)
        elif game_type == "no_corners":
            return game.GameState.no_corners()
        elif game_type == "no_corners_small":
            return game.GameState.no_corners_small()
        else:
            k = min(board_size)
            return game.GameState.empty(board_size, k)

    def create_board(self):
        self.clear_widgets()

        board_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        board_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Calculate button size based on window size and board dimensions
        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height()
        min_dimension = min(window_width, window_height) - 100  # Subtract some padding
        button_size = min_dimension // max(self.game_state.w, self.game_state.h)

        for i in range(self.game_state.h):
            row = []
            for j in range(self.game_state.w):
                button = tk.Button(board_frame, text='', width=3, height=1,
                                   command=lambda x=j, y=i: self.on_click(x, y),
                                   font=self.game_font, bg="white", fg="black",
                                   relief=tk.SOLID, borderwidth=1)
                button.grid(row=i, column=j, padx=2, pady=2)
                button.configure(width=button_size//30, height=button_size//60)  # Adjust button size
                row.append(button)
            self.buttons.append(row)

        # Center the board
        board_frame.pack_propagate(False)
        board_frame.configure(width=button_size * self.game_state.w + 40, height=button_size * self.game_state.h + 40)

    def on_click(self, x, y):
        if self.game_mode.get() == "human_vs_ai" and self.game_state.next_player == game.X_PIECE:
            if self.game_state.is_valid_move((x, y)):
                self.make_move((x, y))
                if not self.check_game_over():
                    self.master.after(1000, self.make_ai_move)

    def make_move(self, move):
        x, y = move
        self.game_state = self.game_state.make_move(move)
        self.buttons[y][x].config(text=self.game_state.board[x][y])
        self.update_info_label()

    def make_ai_move(self):
        def ai_move_thread():
            current_agent = self.player_agent if self.game_state.next_player == game.X_PIECE else self.ai_agent
            move = current_agent.choose_move(self.game_state, time_limit=1.0)
            self.master.after(0, lambda: self.make_move(move))
            if not self.check_game_over() and self.game_mode.get() == "ai_vs_ai":
                self.master.after(1000, self.make_ai_move)

        threading.Thread(target=ai_move_thread).start()

    def update_info_label(self):
        if self.game_mode.get() == "human_vs_ai":
            x_player = "Human"
            o_player = "MinimaxAgent" if self.ai_type.get() == "minimax" else "Random Agent"
        else:  # AI vs AI
            x_player = "MinimaxAgent" if self.ai_type.get() == "minimax" else "Random Agent"
            o_player = "Random Agent" if self.ai_type.get() == "minimax" else "MinimaxAgent"
        
        player_info_text = f"X: {x_player} | O: {o_player}"
        self.player_info_label.configure(text=player_info_text)

        turn_text = f"Next player: {self.game_state.next_player}"
        self.turn_label.configure(text=turn_text)

    def check_game_over(self):
        winner = self.game_state.winner()
        if winner is not None:
            if winner == "draw":
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {winner} wins!")
            self.master.after(1000, self.reset_game)
            return True
        return False

    def reset_game(self):
        self.clear_widgets()
        self.create_menu()

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.buttons = []
        self.info_frame = None
        self.player_info_label = None
        self.turn_label = None

def play_game():
    root = ctk.CTk()
    root.title("K-in-a-Row")
    KInARowGUI(root)
    root.mainloop()

if __name__ == "__main__":
    play_game()

import tkinter as tk
import center_tk_window as ctw
# Importing the custom chess piece classes and the board
import ChessComponents

# All of the visuals is included in the ChessComponents/board.py file. The class in this file called GameBoard hosts the game.

# Initialising the board
playWindow = tk.Tk() # Root window is created
playWindow.title("Chess Game") # Title added
side_size = 200 # This affects the amount of space on the right of the board (200 is needed)
board = ChessComponents.GameBoard(playWindow,side_size=side_size) # Initialising the game board within the root window
board.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying (in TkInter everything to be displayed in a window needs to be either "packed" or "placed"
playWindow.resizable(width=False, height=False) # This locks the size of the window so it cant be resized
playWindow.geometry(str(board.size*8+side_size)+"x"+str(board.size*8)) # This locks the geometry including side_size to encompass the visuals
ctw.center_on_screen(playWindow) # This is a nifty module that centers the window for us. There might be a better way to do it but it happens once at the start of the game
board.Defaults() # This actually initialises the chess game and adds all of the pieces etc

# As with most GUIs the game runs out of the host object which in this case is a GameBoard called board.
# All the logic required to run a game of chess is included in either board or the chess piece objects it contains.
# By calling mainloop() on the tkinter window we allow the buttons to run the game with no further code required here,
playWindow.mainloop()

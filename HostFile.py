import tkinter as tk
import center_tk_window as ctw
# Importing the custom chess piece classes and the board
import ChessComponents

# Initialising the board
playWindow = tk.Tk() # Root window is created
playWindow.title("Chess Game")
side_size = 200 # This affects the amount of space on the right of the board
board = ChessComponents.GameBoard(playWindow,side_size=side_size) # Initialising the game board within the root window
board.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying
playWindow.resizable(width=False, height=False) # This is a very important line that stops the window being edited which makes the layout much easier
# Setting the geometry to include all of the buttons.
# I will need to find a better way of doing this
playWindow.geometry(str(board.size*8+side_size)+"x"+str(board.size*8))
ctw.center_on_screen(playWindow) # This is a nifty module that centers the window for us
board.defaults() # Setting the board for the start of a game

playWindow.mainloop() # Main loop is set here

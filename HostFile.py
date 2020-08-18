# Attempting to make a basic chess game whereby the computer randomly selects a next move.
# This will form the framework for a later project that looks to pit a manual algorithm against a neural network (probably NEAT)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Some variables to set the chess board apprearance
boardSize = 8 # This is a square size (boardSize x boardSize)
boardImage = np.zeros((boardSize,boardSize)) # Store the board in an array
boardImage[1::2,0::2] = 1 # Every other row has every other line as a 1
boardImage[0::2,1::2] = 1 # The opposite with an offset
row_label = col_label = range(boardSize) # creating some labels
plt.imshow(boardImage,cmap="binary") # Plotting the board with black and white squares
plt.show()
import pandas as pd
import numpy as np

class Rook():
    def __init__(self,piece_id):
        # Initialising the piece as a king
        self.type = piece_id[0] # pnkbqrPNKBQR
        self.id = piece_id[1] # Number
        if self.type.isupper():
            self.colour = "w" # White
        else:
            self.colour = "b" # Black
        self.check = False
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        print("Hi I'm a rook")

    def updatemoves(self,squarex,squarey,boardarray):
        t = 1

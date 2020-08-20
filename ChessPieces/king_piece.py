class King():
    def __init__(self,piece_id):
        self.type = piece_id[0] #pnkbqrPNKBQR
        self.id = piece_id[1]
        if self.type.isupper():
            self.colour
        self.check = False
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])

        # Now we set the default positions of the piece depending on what type it is at the start of the game
        if self.id == "p" or self.id == "P": # Then it is a pawn
            # self.moves[]
            t = 1
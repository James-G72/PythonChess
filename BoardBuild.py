<<<<<<< HEAD
import tkinter as tk
import center_tk_window as ctw

class GameBoard(tk.Frame):
    def __init__(self, parent, size=10, rows=8, columns=8, color1="black", color2="white"):
        # Can be customised

        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}

        c_width = columns * size
        c_height = rows * size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=c_width, height=c_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # this binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)

    def addpiece(self, name, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)

    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")


playWindow = tk.Tk()
board = GameBoard(playWindow,80)
board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
ctw.center_on_screen(playWindow)
playWindow.mainloop()
=======

import re
import PIL.Image as image
import PIL.ImageDraw as ImageDraw


class BadChessboard(ValueError):
    pass


def expand_blanks(fen):

    def expand(match):
        return ' ' * int(match.group(0))

    return re.compile(r'\d').sub(expand,fen)


def check_valid(expanded_fen):
    '''Asserts an expanded FEN string is valid'''
    match = re.compile(r'([KQBNRPkqbnrp ]{8}/){8}$').match
    if not match(expanded_fen+'/'):
        raise BadChessboard()


def expand_fen(fen):
    '''Preprocesses a fen string into an internal format.

    Each square on the chessboard is represented by a single
    character in the output string. The rank separator characters
    are removed. Invalid inputs raise a BadChessboard error.
    '''
    expanded = expand_blanks(fen)
    check_valid(expanded)
    return expanded.replace('/','')


def draw_board(n=8,sq_size=(20,20)):
    '''Return an image of a chessboard.

    The board has n x n squares each of the supplied size.'''
    from itertools import cycle
    def square(i,j):
        return i * sq_size[0],j * sq_size[1]

    opaque_grey_background = 192,255
    board = image.new('LA',square(n,n),opaque_grey_background)
    draw_square = ImageDraw.Draw(board).rectangle
    whites = ((square(i,j),square(i+1,j+1))
              for i_start,j in zip(cycle((0,1)),range(n))
              for i in range(i_start,n,2))
    for white_square in whites:
        draw_square(white_square,fill='white')
    return board


class DrawChessPosition(object):
    '''Chess position renderer.

    Create an instance of this class, then call
    '''

    def __init__(self):
        '''Initialise, preloading pieces and creating a blank board.'''
        self.n = 8
        self.create_pieces()
        self.create_blank_board()

    def create_pieces(self):
        '''Load the chess pieces from disk.

        Also extracts and caches the alpha masks for these pieces.
        '''
        black_pieces = 'bknpq'
        white_pieces = 'BKNPQ'
        piece_images = dict()
        for x in range(0,len(black_pieces)):
            black_index = black_pieces[x]
            white_index = white_pieces[x]
            piece_images[black_index] = image.open('Pieces/'+black_index+'b.png')
            piece_images[white_index] = image.open('Pieces/'+black_index+'w.png')
        piece_sizes = set(piece.size for piece in piece_images.values())
        # Sanity check: the pieces should all be the same size
        assert len(piece_sizes) == 1
        self.piece_w,self.piece_h = piece_sizes.pop()
        self.piece_images = piece_images
        self.piece_masks = dict((pc,img.split()[3]) for pc,img in self.piece_images.items())

    def create_blank_board(self):
        '''Pre-render a blank board.'''
        self.board = draw_board(sq_size=(self.piece_w,self.piece_h))

    def point(self,i,j):
        '''Return the top left of the square at (i, j).'''
        w,h = self.piece_w,self.piece_h
        return i * h,j * w

    def square(self,i,j):
        '''Return the square at (i, j).'''
        t,l = self.point(i,j)
        b,r = self.point(i+1,j+1)
        return t,l,b,r

    def draw(self,fen):
        '''Return an image depicting the input position.

        fen - the first record of a FEN chess position.
        Clients are responsible for resizing this image and saving it,
        if required.
        '''
        board = self.board.copy()
        pieces = expand_fen(fen)
        images,masks,n = self.piece_images,self.piece_masks,self.n
        pts = (self.point(i,j) for j in range(n) for i in range(n))

        def not_blank(pt_pc):
            return pt_pc[1] != ' '

        for pt,piece in filter(not_blank,zip(pts,pieces)):
            board.paste(images[piece],pt,masks[piece])
        return board

renderer = DrawChessPosition()
fen = "r2q1rk1/pp2ppbp/1np2np1/2Q3B1/3PP1b1/2N2N2/PP3PPP/3RKB1R"
board = renderer.draw(fen)
board.show()
board.save("%s.png" % fen.replace('/', '-'))
>>>>>>> origin/master

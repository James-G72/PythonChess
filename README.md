# PythonChess
This is a chess game made using TkInter. To run the game stockfish must be installed as an excecutable.
The code uses a class system and is run from HostFile.py.

<img width="952" alt="Screenshot 2020-08-23 at 12 14 39" src="https://user-images.githubusercontent.com/66065325/90977062-67c44000-e53a-11ea-943c-d1644a1bcf2a.png">

## Current Functionality
* The computer cannot play itself properly but the player can play against either Stockfish or a random move generator
* There is no way for the game to end as taking pieces has no significance and the king class has no check logic coded
* The current stockfish wrapper has the ability to return board assesments in favour of either black or white which could be used for training

## Known Issues
* Clicking off the board when selecting a piece removes all highlighting but doesn't deselect the piece which is confusing
* The game cannot currently be run without having stockfish downloaded and converted to an excecutable (even if stockfish isn't used). This code should be moved inside a specific method to prevent it from stopping the game being used for 2 players.
# PyRacer
Simple 2D racing game in Python written with Python Arcade library
# Installation
Game requirements are included in `requirements.txt` file, install them with `pip install -r requirements.txt`.
# Usage
Run the game with `python main.py`. Right now the game uses first joystick it finds to drive the car. If it finds no joystick connected it will print out error and exit.
# Track
To change the map simply switch filename in line `game = MyGame("PyRacer", "test.csv")` (one of the last lines in `main.py`) to your new track file.
## Track file structure
First line of the track is float representing scale. Normally you should work somewhere between 0.75 and 0.5.

Second line is starting position of the car in form `starting_row,starting_column,starting_angle`. `starting_row` and `starting_column` are 0-based values, while `starting_angle` is angle in degrees the car should be pointing, `0` being straight top, `-90` being right.

After that there should be `N` lines of `M` comma separated values each. `N` lines being rows of the track and `M` values being columns of the track. If given tile should be empty the value should be ommited. If given tile should load track sprite it should contain it's name. Track tiles are placed in `sprites/track-texture` directory.
# TODO
* Collision detection
* Distance to wall(s) calculation
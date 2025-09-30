# Game of Life

Python program for simulating Conway's Game of Life and other cellular automata made by Wren Kohler and designed for Python 3.6. Generates gif for user based on desired parameters. 

User can choose to start the simulation using a random grid of size and density specified by the user, or can start the simulation using an RLE (Run Length Encoded) formatted file (with .rle file extension) with a specified minimum grid size. Once the grid has been generated or parsed from file, the program asks the user for the number of generations to run and what life rules to use (not limited to only Conway's Life). If unfamiliar with the B/S rulestring format for various cellular automaton rules, visit [LifeWiki](https://www.conwaylife.com/wiki/Cellular_automaton#Rules). 

With the meaningful simulation parameters out of the way, the program will next ask if the gif should be rendered with or without gridlines visible (purely an aesthetic option), and what frame rate to use for the gif. Program will then generate the simulation and save a gif in a "GoL-gifs" folder. The program will finally ask the user if they want to save an RLE file translating the grid it has just simulated, saving a .rle file in a "saved-RLEs" folder. 

Designed for use from the terminal. User can also change the color scheme of the gifs by changing the GRID_CMAP variable in the python file to any desired colormap.

## Installation

1. Copy the GameOfLife.py file from the repository (the other files are optional)
2. Make sure you have Python version 3.6 or later
3. Make sure you have up to date versions of the following libraries: `matplotlib`, `numpy`, `seaborn`, `celluloid`

## Usage

From terminal, two options for usage.

To use a random starting grid: `python GameOfLife.py`

To use a starting specified RLE file: `python GameOfLife.py <path to RLE file.rle>`

## Example

First, below is an example of a gif created by running the program using a specified RLE file for the Gosper Glider Gun:

![Gosper Glider Gun](GoL-gifs/GosperGliderGun.gif)

Second, below is an example of a gif created using a random grid with 300 generations:

![Random Starting Grid](GoL-gifs/R1ConwaysLife.gif)

## Authors

Wren Kohler

Note: This is a project I did years back in a github account I no longer have access to, so copying repo here to my current account

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

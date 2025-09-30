#!/usr/bin/python

import itertools
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import re
import seaborn as sns
import sys
from celluloid import Camera
from itertools import groupby

"""
Author: Wren Kohler
Description: This file creates a simulation gif of Conway's Game of Life

    Run from command line:
        python GameOfLife.py {optional: RLEfile.rle}

    RLE text file is optional
"""

GRID_CMAP = "tab20_r"
# Some other good cmaps: PuRd, BuPu, Wistia, tab20b_r

def addSpace(grid, desiredSize):
    """
    Adds cells to grid if grid needs to be resized larger
    """
    expandedGrid = grid.copy()
    extraRows = desiredSize[0] - grid.shape[0]
    extraCols = desiredSize[1] - grid.shape[1]
    if extraRows < 0:
        extraRows = 0
    if extraCols < 0:
        extraCols = 0
    for i in range(extraRows // 2):
        expandedGrid = np.append(
            expandedGrid,
            [[0 for i in range(expandedGrid.shape[1])]],
            axis = 0
        )
        expandedGrid = np.append(
            [[0 for i in range(expandedGrid.shape[1])]],
            expandedGrid,
            axis = 0
        )
    for i in range(extraCols // 2):
        expandedGrid = np.append(
            expandedGrid,
            np.array([0 for i in range(expandedGrid.shape[0])])[:,None],
            axis = 1
        )
        expandedGrid = np.append(
            np.array([0 for i in range(expandedGrid.shape[0])])[:,None],
            expandedGrid,
            axis = 1
        )
    return expandedGrid


def checkArray(g, r, c):
    """
    Check cell in grid g at row r and column c to see if it is a valid location,
    otherwise it is treated as a dead cell
    """
    if r < 0:
        r = g.shape[0] + 1
    if c < 0:
        c = g.shape[1] + 1
    #Check for index out of bounds
    try:
        nVal = g[r][c]
    except IndexError:
        nVal = 0
    return nVal


def createAnimation(inGrid, gridSize, generations, rulestring):
    """
    Executes {generations} number of time step updates to model the Game of Life
    while also taking snapshots to compile into an animation at the end
    """
    if not os.path.exists("GoL-gifs"): os.mkdir("GoL-gifs")
    filename = unique_file("GoL-gifs/LifeSim".format(generations), "gif")

    gridOn = input('Do you want to see gridlines? (y/n) ')
    while (gridOn != 'y') and (gridOn != 'n'):
        gridOn = input('Do you want to see gridlines? (y/n) ')

    fps = input('Please enter desired gif frame rate (ex. 5, 10, etc.): ')
    while not fps.isdigit():
        fps = input('Enter desired gif frame rate as an integer (ex. 5, 10, etc.): ')

    if int(fps) <= 0:
        fps = 1
    Writer = animation.writers['pillow']
    writer = Writer(fps=int(fps), metadata=dict(artist='Me'), bitrate=1800)

    if (inGrid.shape[0] < gridSize[0]) or (inGrid.shape[1] < gridSize[1]):
        grid = addSpace(inGrid, gridSize)
    else:
        grid = inGrid.copy()

    fig = plt.figure()
    fig.set_size_inches(8, 8)
    camera = Camera(fig)
    if (gridOn == 'y'):
        ax = plt.gca();
        ax.set_xticks(np.arange(-.5, gridSize[1], 1), minor=True);
        ax.set_yticks(np.arange(-.5, gridSize[0], 1), minor=True);
        ax.grid(which='minor', color='w', linestyle='-', linewidth=2)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    else:
        plt.axis('off')
    plt.annotate(
        'Generation (0/{})...'.format(generations),
        xy=(50, 30),
        xycoords='figure pixels',
        size=20
    )
    plt.imshow(grid, cmap=GRID_CMAP)
    camera.snap()

    for i in range(generations):
        plt.annotate(
            'Generation ({}/{})...'.format(i+1, generations),
            xy=(50, 30),
            xycoords='figure pixels',
            size=20
        )
        if (gridOn == 'y'):
            ax = plt.gca();
            ax.set_xticks(np.arange(-.5, gridSize[1], 1), minor=True);
            ax.set_yticks(np.arange(-.5, gridSize[0], 1), minor=True);
            ax.grid(which='minor', color='w', linestyle='-', linewidth=2)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
        else:
            plt.axis('off')
        plt.imshow(updateGrid(grid, rulestring), cmap=GRID_CMAP)
        camera.snap()
        print('Generation ({}/{})...'.format(i+1, generations))

    print()
    print('Creating animation... Please wait...')
    ani = camera.animate()
    ani.save(filename, writer = writer)
    print("Done! Saved as {}".format(filename))
    print()


def encodeGrid(grid, top, bot, minCol, maxCol):
    """
    Encodes a grid into a grouping list of RLE tags and counts
    """
    RLEtups = []
    for row in range(top, bot + 1):
        cellCount = 0
        rowString = ''
        for col in range(minCol, maxCol + 1):
            cell = grid[row][col]
            rowString += 'o' if cell == 1 else 'b'
        groups = [(label, sum(1 for _ in group)) for label, group in groupby(rowString)]
        RLEtups += groups
        if row != bot:
            RLEtups += [('$', 1)]
        else:
            RLEtups +=  [('!', 1)]

    #Condense encoded Strings per RLE formatting guidelines
    possibleOptimization = True
    while possibleOptimization == True:
        possibleOptimization = False
        indicesToPop = []
        for i in range(len(RLEtups)):
            if (i < len(RLEtups) - 1):
                if (RLEtups[i + 1][0] in ['$', '!'] and RLEtups[i][0] == 'b'):
                    indicesToPop.append(i)
                if (RLEtups[i][0] == RLEtups[i + 1][0]):
                    RLEtups[i + 1] = (RLEtups[i][0], (RLEtups[i][1] + RLEtups[i + 1][1]))
                    indicesToPop.append(i)
        if (len(indicesToPop) > 0):
            possibleOptimization = True
            #delete multiple indices at once
            for j in sorted(indicesToPop, reverse=True):
                del RLEtups[j]

    return RLEtups


def findBoundaries(grid):
    """
    Finds meaningful top, bottom, right, and left boundaries of grid to be used
    in RLE encoding
    """
    for top in range(grid.shape[0]):
        if sum(grid[top]) > 0:
            break
    for bot in range(grid.shape[0]-1, -1, -1):
        if sum(grid[bot]) > 0:
            break
    minCol = math.inf
    maxCol = -math.inf
    for row in range(top, bot + 1):
        for col in range(grid.shape[1]):
            if grid[row][col] == 1:
                if col < minCol:
                    minCol = col
                elif col > maxCol:
                    maxCol = col
        if (minCol == 0) and (maxCol == grid.shape[1] - 1):
            #min is first column, and max is last column
            #so no need to keep looping
            break
    return top, bot, minCol, maxCol


def findNeighbors(g, r, c):
    """
    Check all neighbors of cell at row r, column c in grid g to find the count
    of all living neighbor cells
    """
    nAlive = checkArray(g, r-1, c-1) + checkArray(g, r-1, c) + \
        checkArray(g, r-1, c+1) + checkArray(g, r+1, c-1) + \
        checkArray(g, r+1, c) + checkArray(g, r+1, c+1) + \
        checkArray(g, r, c-1) + checkArray(g, r, c+1)
    return nAlive


def parseInput(args):
    """
    Parses command line arguments to see if RLE file supplied, or if using a
    randomly generated grid
    """
    gridHInput = input('Please enter desired minimum grid height: ')
    while not gridHInput.isdigit():
        gridHInput = input('Please enter desired minimum grid height: ')
    gridWInput = input('Please enter desired minimum grid width: ')
    while not gridWInput.isdigit():
        gridWInput = input('Please enter desired minimum grid width: ')
    # gridSize is height by width (rows by cols)
    gridSize = (int(gridHInput), int(gridWInput))

    if (len(args) == 2):
        #supplied RLE file
        initialGrid, rulestring = parseRLE(args[1])
    else:
        #create a random grid
        gridLive = input('Please enter percent of alive cells (ex: 40, 60, etc.): ')
        while not gridLive.isdigit():
            gridLive = input('Please enter percent of alive cells (ex: 40, 60, etc.): ')
        initialGrid = randomGrid(gridSize[0], gridSize[1], int(gridLive))
        #create rulestring
        lifeChoice = input('Do you want to use default Game of Life rules? (y/n) ')
        while (lifeChoice != 'y') and (lifeChoice != 'n'):
            lifeChoice = input('Do you want to use default Game of Life rules? (y/n) ')
        if lifeChoice == 'y':
            #default Game of Life rulestring
            rulestring = 'B3/S23'
        else:
            birthstring = input('Please enter desired birth rule (ex. 23): ')
            while not birthstring.isdigit():
                birthstring = input('Please enter desired birth rule (ex. 23): ')
            survivestring = input('Please enter desired survive rule (ex. 23): ')
            while not survivestring.isdigit():
                survivestring = input('Please enter desired survive rule (ex. 23): ')
            rulestring = 'B{}/S{}'.format(birthstring, survivestring)

    generationInput = input('Please enter desired number of generations: ')
    while not generationInput.isdigit():
        generationInput = input('Please enter desired number of generations: ')
    generations = int(generationInput)

    return initialGrid, gridSize, generations, rulestring


def parseRLE(filename):
    """
    Parses an RLE text file passed in as filename, into a grid
    """
    with open(filename) as f:
        content = [line.strip() for line in f]
    RLEstring = ''
    for line in content:
        if line[0] == '#':
            #comment line
            continue
        elif line[0] == 'x':
            #rule line
            chunks = line.split(',')
            xvalue = int(chunks[0].strip().split('=')[1])
            yvalue = int(chunks[1].strip().split('=')[1])
            rulestring = chunks[2].split('=')[1].strip()

        else:
            RLEstring += line
        if line[-1] == '!':
            RLEstring = RLEstring[:-1]
            break

    grid = []
    for chunk in RLEstring.split('$'):
        RLEtags = re.findall(r'[bo]',chunk)
        tagCounts = re.split(r'[bo]',chunk)
        gridLine = []
        for i in range(len(RLEtags)):
            curTag = RLEtags[i]
            try:
                curCt = int(tagCounts[i])
            except ValueError:
                curCt = 1
            if curTag == 'b':
                gridLine.extend([0 for k in range(curCt)])
            else:
                gridLine.extend([1 for k in range(curCt)])

        if len(gridLine) != xvalue:
            #fill to end of line
            gridLine.extend([0 for i in range(xvalue - len(gridLine))])
        grid.append(gridLine)
        if (tagCounts[-1] != ''):
            #account for gap lines
            for j in range(int(tagCounts[-1]) - 1):
                grid.append([0 for k in range(xvalue)])
    return np.array(grid), rulestring


def parseRules(rulestring):
    """
    Parses rulestring into its birth and survive components (assuming B/S notation)
    """
    birthChunk = list(rulestring.split("/")[0].split('B')[1])
    surviveChunk = list(rulestring.split("/")[1].split('S')[1])
    if len(birthChunk) == 0:
        birthRule = []
    else:
        birthRule = [int(i) for i in birthChunk]
    if len(surviveChunk) == 0:
        surviveRule = []
    else:
        surviveRule = [int(i) for i in surviveChunk]

    return birthRule, surviveRule


def randomGrid(W, H, live):
    """
    Generates a random grid of size W*H with p[0]% dead cells, p[1]% alive cells
    """
    pLive = live / 100
    pDead = 1 - pLive
    return np.random.choice([0,1], W*H, p=[pDead, pLive]).reshape(W, H)


def saveRLE(grid, rule):
    """
    Prompt and save RLE text file of starting grid
    """
    save = input('Do you want to save RLE file of starting state? (y/n) ')
    while (save != 'y') and (save != 'n'):
        save = input('Do you want to save RLE file of starting state? (y/n) ')
    if save == 'y':
        writeRLE(grid, rule)


def unique_file(basename, ext):
    """
    Finds unique filename with given base and extension to avoid overwriting
    """
    actualname = '{}.{}'.format(basename, ext)
    c = itertools.count()
    while os.path.exists(actualname):
        actualname = '{}_{}.{}'.format(basename, next(c), ext)
    return actualname


def updateGrid(grid, rulestring):
    """
    Executes a single generation time step according to the rules specified in
    rulestring, and updates grid accordingly
    """
    nextGrid = grid.copy()
    birthRule, surviveRule = parseRules(rulestring)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            #boundary check
            nAlive = 0
            nAlive = findNeighbors(grid, i, j)

            nextState = 0
            if grid[i][j] == 1:
                #alive cell, check for survive
                if (nAlive in surviveRule):
                    #lives on
                    nextState = 1
                else:
                    #underpopulation or overpopulation
                    nextState = 0
            else:
                #dead cell, check for birth
                if (nAlive in birthRule):
                    #reproduces
                    nextState = 1
                else:
                    #stays dead
                    nextState = 0

            #build grid of next states
            nextGrid[i][j] = nextState

    grid[:] = nextGrid[:]
    return grid


def writeRLE(grid, rule):
    """
    Writes grid out to a text file in RLE format
    """
    if not os.path.exists("saved-RLEs"): os.mkdir("saved-RLEs")
    filename = unique_file("saved-RLEs/RLEfile", "rle")
    f = open(filename, "w")
    top, bot, minCol, maxCol = findBoundaries(grid)
    #write x,y header
    f.write('x = {}, y = {}, rule = {}\n'.format(str(maxCol - minCol + 1), str(bot - top + 1), rule))
    RLEgroups = encodeGrid(grid, top, bot, minCol, maxCol)
    finishedWriting = False
    allLines = []
    individualLine = ''
    pos = 0
    #write grid with 70 character lines
    while finishedWriting == False:
        if (RLEgroups[pos][1] == 1):
            #single cell
            if (1 + len(individualLine) > 70):
                #new line
                individualLine += '\n'
                f.write(individualLine)
                individualLine = RLEgroups[pos][0]
            else:
                #same line
                individualLine += RLEgroups[pos][0]
        else:
            if (len(str(RLEgroups[pos][1])) + len(individualLine) + 1 > 70):
                #new line
                individualLine += '\n'
                f.write(individualLine)
                individualLine = str(RLEgroups[pos][1]) + RLEgroups[pos][0]
            else:
                #same line
                individualLine += str(RLEgroups[pos][1]) + RLEgroups[pos][0]
        if (pos == len(RLEgroups) - 1):
            f.write(individualLine)
            finishedWriting = True
        else:
            pos += 1
    f.close()
    print('Done! RLE info saved to {}'.format(filename))



if __name__ == '__main__':
    """
    Generates simulation and gif animation of Game of Life, allows user
    to write out RLE file corresponding to grid
    """
    initialGrid, gridSize, generations, rulestring = parseInput(sys.argv)
    #save starting state in case user wants to write out RLE later
    startingState = initialGrid.copy()
    createAnimation(initialGrid, gridSize, generations, rulestring)
    saveRLE(startingState, rulestring)

    sys.exit(0)

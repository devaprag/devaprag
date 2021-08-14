#!/usr/bin/env python
# coding: utf-8

import functools

# --------------
# globals
# --------------

kScale = 3
kScaleSq = kScale * kScale
kScaleCube = kScaleSq * kScale

# -----------------------------
# index getters (non-modifying)
# -----------------------------


@functools.cache
def get_row(gridIndex):
    """ get all cells in same row
        gridIndex is cell index 0->kScaleCube (eg 80 for kScale = 3)
        use grid[gridIndex] to get the cell value

    ... ... ...
    xxi xxx xxx
    ... ... ...

    ... ... ...
    ... ... ...
    ... ... ...

    ... ... ...
    ... ... ...
    ... ... ...

    """
    offset = (gridIndex // kScaleSq) * kScaleSq
    return set([a for a in range(offset, offset + kScaleSq)])


@functools.cache
def get_column(gridIndex):
    """ get all cells in same column

    ..x ... ...
    ..i ... ...
    ..x ... ...

    ..x ... ...
    ..x ... ...
    ..x ... ...

    ..x ... ...
    ..x ... ...
    ..x ... ...

    """
    offset = gridIndex % kScaleSq
    return set([a for a in range(offset, offset + kScaleSq * kScaleSq, kScaleSq)])


@functools.cache
def transformFn():
    """ mirrored transform function (works both ways)
        grid index <--> frame index

       grid indexes

         frame 0      frame 1      frame 2
       [0,  1,  2,   3,  4,  5,   6,  7,  8,
        9, 10, 11,  12, 13, 14,  15, 16, 17,
       18, 19, 20,  21, 22, 23,  24, 25, 26,

         frame 3      frame 4      frame 5
       27, 28, 29,  30, 31, 32,  33, 34, 35,
       36, 37, 38,  39, 40, 41,  42, 43, 44,
       45, 46, 47,  48, 49, 50,  51, 52, 53,

         frame 6      frame 7      frame 8
       54, 55, 56,  57, 58, 59,  60, 61, 62,
       63, 64, 65,  66, 67, 68,  69, 70, 71,
       72, 73, 74,  75, 76, 77,  78, 79, 80]

      frame indexes

      frame 0 : [0,  1,  2,   9, 10, 11,  18, 19, 20,
      frame 1 :  3,  4,  5,  12, 13, 14,  21, 22, 23,
      frame 2 :  6,  7,  8,  15, 16, 17,  24, 25, 26,

      frame 3 : 27, 28, 29,  36, 37, 38,  45, 46, 47,
      frame 4 : 30, 31, 32,  39, 40, 41,  48, 49, 50,
      frame 5 : 33, 34, 35,  42, 43, 44,  51, 52, 53,

      frame 6 : 54, 55, 56,  63, 64, 65,  72, 73, 74,
      frame 7 : 57, 58, 59,  66, 67, 68,  75, 76, 77,
      frame 8 : 60, 61, 62,  69, 70, 71,  78, 79, 80]
    """
    frameIndexes = []
    for w in range(kScale):
        for z in range(kScale):
            for y in range(kScale):
                for x in range(kScale):
                    frameIndexes.append(
                        x + kScale * z + kScaleSq * y + kScaleCube * w)
    return frameIndexes


@functools.cache
def get_frame_neighbours(frameIndex):
    """ get all cells in same frame (using frame index)
    """
    start = (frameIndex // kScaleSq) * kScaleSq
    return range(start, start + kScaleSq)


@functools.cache
def get_neighbours(gridIndex):
    """ get all cells in same frame

    xxx ... ...
    xxi ... ...
    xxx ... ...

    ... ... ...
    ... ... ...
    ... ... ...

    ... ... ...
    ... ... ...
    ... ... ...
    """
    transform = transformFn()
    return set([transform[a] for a in get_frame_neighbours(transform[gridIndex])])


@functools.cache
def get_buddy_remove(gridIndex, getFn):
    """  if value is in buddies and not in others, 
         can remove value from 'removeFrom'

     key

     x - buddies
     o - others
     r - removeFrom

     bbb rrr rrr
     ooo ... ...
     ooo ... ...

     ... ... ...
     ... ... ...
     ... ... ...

     ... ... ...
     ... ... ...
     ... ... ...
    """

    # b + r
    line = getFn(gridIndex)

    # b + o
    frame = get_neighbours(gridIndex)

    # b - buddies
    buddies = line.intersection(frame)

    # o - others
    others = frame.difference(buddies)

    # r - removeFrom
    removeFrom = line.difference(buddies)

    return buddies, others, removeFrom


# --------------
# utils
# --------------

def flatten(s):
    """ util method to make container 1 dimensional
    """
    return [y for x in s for y in x]

# --------------
# smart checkers
# --------------


def deduce_from_other_values(grid, index, getFn):
    """ if potential value is not in any other cell in row/column
        that cell must be that value
        return value, or None
    """
    consolidated_other_potentials = set(
        flatten([grid[i] for i in getFn(index) if index != i]))
    for potential in grid[index]:
        if potential not in consolidated_other_potentials:
            return potential
    return None


def deduce_from_buddies(grid, gridIndex, getFn):
    """ if value is in buddies and not in others,
        can remove value from 'removeFrom'
    """
    buddies, others, remove_from = get_buddy_remove(gridIndex, getFn)

    # search for buddy values in others values
    buddy_values = set(flatten([grid[b] for b in buddies]))
    other_values = set(flatten([grid[b] for b in others]))

    remove_values = buddy_values.difference(other_values)
    return remove_values, remove_from


# --------------
# printers
# --------------

def print_score(numSolved):
    print('Score: {}/{} ({:.2f}%)'.format(numSolved, kScaleSq *
                                          kScaleSq, (numSolved / (kScaleSq * kScaleSq)) * 100.0))


def print_grid(grid):
    """ print the grid
    """
    newline = kScaleSq
    line = ""
    for gridIndex in range(len(grid)):
        vals = list(grid[gridIndex])
        if len(vals) == 1:
            line = line + str(vals[0])
        else:
            for v in vals:
                line = line + str(v)
        line = line + ' '

        newline = newline - 1
        if newline == 0:
            newline = kScaleSq
            print(line)
            line = ""


# --------------
# modifiers
# --------------

def bomb(grid, index, value):
    """ once a cell is known, we can eliminate the same value
        from that row, column and frame. Kaboom
    """
    if value not in grid[index]:
        print('Error: value {} not in potentials {} for index {}'.format(
            value, grid[index], index))

    for i in get_neighbours(index).union(get_row(index), get_column(index)):
        grid[i].discard(value)

    # re-instate known cell value
    grid[index] = {value}


def gentle_remove(grid, index, value):
    """ just remove value from the one cell
    """
    grid[index].discard(value)


def single_cell_strategy(grid, gridIndex, getFn):
    """ if potential value is not in any other cell in row/column
        that cell must be that value
    """
    deduced_value = deduce_from_other_values(grid, gridIndex, getFn)
    if deduced_value is not None:
        bomb(grid, gridIndex, deduced_value)


def buddy_strategy(grid, gridIndex, getFn):
    """ if value is in buddies and not in others,
        can remove value from 'remove_from'
    """
    remove_values, remove_from = deduce_from_buddies(grid, gridIndex, getFn)
    for v in remove_values:
        for r in remove_from:
            gentle_remove(grid, r, v)


# --------------
# solution loop
# --------------

def solve(grid):
    numSolved = 0
    for gridIndex in range(len(grid)):
        if len(grid[gridIndex]) == 1:
            numSolved = numSolved + 1
            [val] = grid[gridIndex]  # unpack single value
            bomb(grid, gridIndex, val)
        else:
            # single cell strategy
            for fn in [get_row, get_column, get_neighbours]:
                single_cell_strategy(grid, gridIndex, fn)

            # buddy cell strategy
            for fn in [get_row, get_column]:
                buddy_strategy(grid, gridIndex, fn)

    return numSolved


def loop_solution(grid, max_attempts, verbose):
    prev_score = 0
    for num_attempts in range(max_attempts):
        num_solved = solve(grid)
        if verbose:
            print_grid(grid)

        print_score(num_solved)

        if prev_score == num_solved:
            return False
        prev_score = num_solved

        if (num_solved == kScaleSq * kScaleSq):
            return True

    return False


# --------------
# grid setup
# --------------

def default_grid():
    """ grid is ALL (kScaleSq * kScaleSq) cells
        each cell contains set of potential values
    """
    grid = []

    potentials = set([r + 1 for r in range(kScaleSq)])

    # populate grid with potential values
    for s in range(kScaleSq * kScaleSq):
        grid.append(potentials.copy())

    return grid


def initialise_grid(seed, grid):
    """ use initial values from newspaper to eliminate potential values
    """
    for s in range(len(seed)):
        if seed[s] != 0:
            bomb(grid, s, seed[s])


# --------------
# main function
# --------------
def suduko(seed, max_attempts, verbose):
    # grid is ALL (kScaleSq * kScaleSq) cells
    # each cell contains set of potential values
    grid = default_grid()

    # use initial values from newspaper to eliminate potential values
    initialise_grid(seed, grid)

    # the main solution loop
    if not loop_solution(grid, max_attempts, verbose):
        print('Failed :(')
    else:
        print('Success!')

    # finally, print the result
    print_grid(grid)


if __name__ == "__main__":

    # type them in row by row, not frame by frame
    # 0 means not solved
    quiz_gentle = [0, 0, 1, 0, 9, 2, 0, 0, 0, 3, 2, 5, 7, 1, 0, 0, 9, 8, 0, 0, 9, 0, 0, 0, 1, 0, 6, 6, 3, 0, 0, 2, 0, 5, 4, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 1, 0, 5, 0, 8, 0, 0, 0, 0, 0, 7, 0, 0, 3, 5, 4, 8, 0, 2, 0, 0, 0, 0, 6, 8, 3, 0, 9, 2, 0, 0, 0, 0, 9, 6, 5, 0]
    quiz_moderate = [0, 4, 0, 9, 8, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 7, 8, 0, 0, 4, 0, 0, 0, 0, 2, 9, 0, 0, 0, 0,
                     3, 0, 6, 0, 0, 0, 1, 9, 0, 0, 0, 7, 0, 0, 4, 0, 8, 6, 0, 2, 0, 0, 5, 0, 0, 2, 0, 0, 0, 0, 8, 0, 7, 0, 0, 1, 4, 0, 0, 0, 0, 0, 0]
    quiz_easy = [0, 0, 0, 6, 0, 0, 7, 0, 0, 0, 0, 0, 0, 1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 4, 8, 0, 0, 0, 0, 0, 0, 5, 0, 9, 0, 0,
                 0, 6, 0, 0, 0, 1, 3, 0, 1, 9, 0, 0, 4, 0, 0, 0, 7, 0, 1, 0, 0, 5, 3, 0, 5, 0, 0, 0, 3, 6, 0, 0, 8, 0, 0, 0, 0, 0, 0, 9, 7, 0]
    quiz_hard = [0, 0, 9, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1, 0, 2, 7, 0, 0, 0, 0, 0, 0, 0, 7, 1, 0, 2, 0, 0, 5, 0, 0, 3, 0, 0,
                 8, 0, 0, 0, 0, 0, 0, 0, 6, 9, 0, 4, 0, 0, 1, 0, 6, 0, 4, 0, 0, 0, 8, 0, 0, 0, 2, 0, 0, 6, 0, 0, 4, 0, 0, 0, 0, 5, 0, 0, 0, 0]

    max_attempts = 10
    verbose = False
    suduko(quiz_gentle, max_attempts, verbose)
    suduko(quiz_moderate, max_attempts, verbose)
    suduko(quiz_easy, max_attempts, verbose)
    suduko(quiz_hard, max_attempts, verbose)

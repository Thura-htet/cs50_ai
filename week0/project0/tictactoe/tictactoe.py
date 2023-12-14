from copy import deepcopy
"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    num_empty = 0
    for row in board:
        for cell in row:
            if cell == EMPTY:
                num_empty += 1
    if (num_empty % 2) == 0:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_set = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_set.add((i, j))
    return possible_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    copy_board = deepcopy(board)
    copy_board[action[0]][action[1]] = player(board)
    return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in range(3):
        if (board[row][0] != None) and (board[row][0] == board[row][1] == board[row][2]):
            return board[row][0]
    for column in range(3):
        if (board[0][column] != None) and (board[0][column] == board[1][column] == board[2][column]):
            return board[0][column]
    if (board[1][1] != None) and ((board[0][0] == board[1][1] == board[2][2]) or (board[0][2] == board[1][1] == board[2][0])):
        return board[1][1]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        highest_value = -math.inf
        optimal_move = (1, 1)
        for action in actions(board):
            value = min_value(result(board, action))
            if value > highest_value:
                highest_value = value
                optimal_move = action
        return optimal_move
    else:
        smallest_value = math.inf
        optimal_move = (1, 1)
        for action in actions(board):
            value = max_value(result(board, action))
            if value < smallest_value:
                smallest_value = value
                optimal_move = action
        return optimal_move
        
def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

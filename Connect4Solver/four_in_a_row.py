# use math library if needed

#Simple python program to implement the minimax, alpha-beta pruning and expectimax algroithm for connect 4.
#Nophil Mehboob 217395609

import math

def get_child_boards(player, board):
    """
    Generate a list of succesor boards obtained by placing a disc 
    at the given board for a given player
   
    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that will place a disc on the board
    board: the current board instance

    Returns
    -------
    a list of (col, new_board) tuples,
    where col is the column in which a new disc is placed (left column has a 0 index), 
    and new_board is the resulting board instance
    """
    res = []
    for c in range(board.cols):
        if board.placeable(c):
            tmp_board = board.clone()
            tmp_board.place(player, c)
            res.append((c, tmp_board))
    return res


def evaluate(player, board):
    """
    This is a function to evaluate the advantage of the specific player at the
    given game board.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the specific player
    board: the board instance

    Returns
    -------
    score: float
        a scalar to evaluate the advantage of the specific player at the given
        game board
    """
    adversary = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    # Initialize the value of scores
    # [s0, s1, s2, s3, --s4--]
    # s0 for the case where all slots are empty in a 4-slot segment
    # s1 for the case where the player occupies one slot in a 4-slot line, the rest are empty
    # s2 for two slots occupied
    # s3 for three
    # s4 for four
    score = [0]*5
    adv_score = [0]*5

    # Initialize the weights
    # [w0, w1, w2, w3, --w4--]
    # w0 for s0, w1 for s1, w2 for s2, w3 for s3
    # w4 for s4
    weights = [0, 1, 4, 16, 1000]

    # Obtain all 4-slot segments on the board
    seg = []
    invalid_slot = -1
    left_revolved = [
        [invalid_slot]*r + board.row(r) + \
        [invalid_slot]*(board.rows-1-r) for r in range(board.rows)
    ]
    right_revolved = [
        [invalid_slot]*(board.rows-1-r) + board.row(r) + \
        [invalid_slot]*r for r in range(board.rows)
    ]
    for r in range(board.rows):
        # row
        row = board.row(r) 
        for c in range(board.cols-3):
            seg.append(row[c:c+4])
    for c in range(board.cols):
        # col
        col = board.col(c) 
        for r in range(board.rows-3):
            seg.append(col[r:r+4])
    for c in zip(*left_revolved):
        # slash
        for r in range(board.rows-3):
            seg.append(c[r:r+4])
    for c in zip(*right_revolved): 
        # backslash
        for r in range(board.rows-3):
            seg.append(c[r:r+4])
    # compute score
    for s in seg:
        if invalid_slot in s:
            continue
        if adversary not in s:
            score[s.count(player)] += 1
        if player not in s:
            adv_score[s.count(adversary)] += 1
    reward = sum([s*w for s, w in zip(score, weights)])
    penalty = sum([s*w for s, w in zip(adv_score, weights)])
    return reward - penalty

#Minimax algorithm, assumes player in first call is the max player
#@param player, the max player
#@param board, the board state to start at
#@param depth_limit, the deepest we would like to search
def minimax(player, board, depth_limit):
    """
    Minimax algorithm with limited search depth.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go further before stopping
    max_player: boolean

    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    max_player = player
    placement = None
    
    #Recursive function to calculate max and min values of each board state below our starting board
    def mongomax(player, board, depth):
        #Next player for recursive call
        next_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
        
        #If end  of branch, return utility
        if depth == 0 or board.terminal():
            return evaluate(player, board)
        
        #If max player choose max of children
        if player == max_player:
            v = -math.inf
            v = evaluate(player,board)
            for state in get_child_boards(player, board):
                #Recursively find max of child states
                v = max(v, mongomax(next_player, state[1], depth-1))
            return v

        #Otherwise if min player do the opposite
        else:
            v = math.inf
            v = evaluate(player,board)

            for state in get_child_boards(player, board):
                score = mongomax(next_player, state[1], depth-1)
              
                v = min(v, score)
            return v

    options = []
    optionsTest = []

    #Our implementation technically does the first 'max' manually, so change players for now
    player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1

    #Find the minimax of all child states of our current states, because this returns up to 7 possible states, at the end we must run a max on this list for the best move to make
    for state in get_child_boards(player, board):
        options.append(mongomax(player, state[1], depth_limit-1))
        optionsTest.append(evaluate(player,state[1]))

    index = 0
    modifiedOptions = []    #The list of states to choose from as a max, just modified to account for non placable columns
    ogMod = []              #The original utility values

    #Our utility values exist for all possible board placements, so we could have only 3 states here later in the game. 
    #We want our list of possible states to be of length 7, so we fill in invalid board locations in the list with -inf
    for i in range(0,7):
        if board.placeable(i):
            modifiedOptions.append(options[index])
            ogMod.append(optionsTest[index])
            index += 1
        else:
            modifiedOptions.append(-math.inf)
            ogMod.append(-math.inf)
    maximum = 0
    maxScore = -math.inf

    #If our initial state was better, prefer the initial
    for i in range(len(modifiedOptions)):
        if modifiedOptions[i] < ogMod[i]:
            modifiedOptions[i] = ogMod[i]

    #Now we do the final root 'max' choice, and pick the largest utility from the board states.
    for i in range(len(modifiedOptions)):
        if modifiedOptions[i] > maxScore:
            maxScore = modifiedOptions[i]
            maximum = i

    placement = maximum #placement is the index of our best/ highest utility option

    
    return placement

#Minimax with pruning algorithm, assumes player in first call is the max player
#@param player, the max player
#@param board, the board state to start at
#@param depth_limit, the deepest we would like to search
def alphabeta(player, board, depth_limit):
    """
    Minimax algorithm with alpha-beta pruning.

     Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go further before stopping
    alpha: float
    beta: float
    max_player: boolean


    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    max_player = player
    placement = None

    #Recursive algorithm for alpha-beta search
    def alphabethaMinimax(player, board, depth, alpha, beta):
        #next player is other player
        next_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
        
        #if end of brach return utility
        if depth == 0 or board.terminal():
            return evaluate(player, board)

        #If max player return max node
        if player == max_player:
            v = -math.inf
            v = evaluate(player,board)
            for state in get_child_boards(player, board):
                v = max(v, alphabethaMinimax(next_player, state[1], depth-1, alpha, beta))
                if v >= beta:
                    break
                a = max(alpha, v)
            return v

        #If min player return min node
        else:
            v = math.inf
            v = evaluate(player,board)
            for state in get_child_boards(player, board):
                v = min(v, alphabethaMinimax(next_player, state[1], depth-1, alpha, beta))
                if v <= alpha:
                    break
                beta = min(beta, v)
            return v

    options = []
    optionsTest = []

    #Our implementation technically does the first 'max' manually, so change players for now
    player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1

    #Find the minimax of all child states of our current states, because this returns up to 7 possible states, at the end we must run a max on this list for the best move to make
    for state in get_child_boards(player, board):
        options.append(alphabethaMinimax(player, state[1], depth_limit-1, -math.inf, math.inf))
        optionsTest.append(evaluate(player, state[1]))

    modifiedOptions = []    #The list of states to choose from as a max, just modified to account for non placable columns
    index = 0
    ogMod = []              #The original utility values

    #Our utility values exist for all possible board placements, so we could have only 3 states here later in the game. 
    #We want our list of possible states to be of length 7, so we fill in invalid board locations in the list with -inf
    for i in range(0,7):
        if board.placeable(i):
            modifiedOptions.append(options[index])
            ogMod.append(optionsTest[index])
            index += 1
        else:
            modifiedOptions.append(-math.inf)
            ogMod.append(-math.inf)

    #If our initial state was better, prefer the initial
    for i in range(len(modifiedOptions)):
        if modifiedOptions[i] < ogMod[i]:
            modifiedOptions[i] = ogMod[i]

    #Now we do the final root 'max' choice, and pick the largest utility from the board states.
    maxScore = -math.inf
    for i in range(len(modifiedOptions)):
        print(maxScore)
        if modifiedOptions[i] > maxScore:
            maxScore = modifiedOptions[i]

            maximum = i

    placement = maximum

    return placement


def expectimax(player, board, depth_limit):
    """
    Expectimax algorithm.
    We assume that the adversary of the initial player chooses actions
    uniformly at random.
    Say that it is the turn for Player 1 when the function is called initially,
    then, during search, Player 2 is assumed to pick actions uniformly at
    random.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go before stopping
    max_player: boolean

    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    max_player = player
    placement = None


    #Recursive function to calculate max and min values of each board state below our starting board
    def expectiman(player, board, depth):
        #Next player for recursive call
        next_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1

        #If end  of branch, return utility
        if depth == 0 or board.terminal():
            return evaluate(player, board)

        #If max player choose max of children 
        if player == max_player:
            v = -math.inf
            #v = evaluate(player,board)
            for state in get_child_boards(player, board):
                v = max(v, expectiman(next_player, state[1], depth-1))
            return v

        #Otherwise if min player take average of children
        else:
            children = get_child_boards(player, board)
            v = 0
            probability = 1 / len(children)
            for state in children:
                v += probability*expectiman(next_player, state[1], depth-1)
            return v

    #Our implementation technically does the first 'max' manually, so change players for now
    player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    options = []
    optionsTest = []

    #Find the minimax of all child states of our current states, because this returns up to 7 possible states, at the end we must run a max on this list for the best move to make
    for state in get_child_boards(player, board):
        options.append(expectiman(player, board, depth_limit-1))
        optionsTest.append(evaluate(player, state[1]))

    index = 0
    modifiedOptions = []        #The list of states to choose from as a max, just modified to account for non placable columns
    ogMod = []                  #The original utility values

    #Our utility values exist for all possible board placements, so we could have only 3 states here later in the game. 
    #We want our list of possible states to be of length 7, so we fill in invalid board locations in the list with -inf
    for i in range(0,7):
        if board.placeable(i):
            modifiedOptions.append(options[index])
            ogMod.append(optionsTest[index])
            index += 1
        else:
            modifiedOptions.append(-math.inf)
            ogMod.append(-math.inf)
    maximum = 0
    maxScore = -math.inf

    #If our initial state was better, prefer the initial
    for i in range(len(modifiedOptions)):
        if modifiedOptions[i] < ogMod[i]:
            modifiedOptions[i] = ogMod[i]
    
    #Now we do the final root 'max' choice, and pick the largest utility from the board states.
    for i in range(len(modifiedOptions)):
        if modifiedOptions[i] > maxScore:
            maxScore = modifiedOptions[i]
            maximum = i

    placement = maximum #placement is the index of our best/ highest utility option

    return placement


if __name__ == "__main__":
    from game_gui import GUI
    import tkinter

    algs = {
        "Minimax": minimax,
        "Alpha-beta pruning": alphabeta,
        "Expectimax": expectimax
    }

    root = tkinter.Tk()
    GUI(algs, root)
    root.mainloop()

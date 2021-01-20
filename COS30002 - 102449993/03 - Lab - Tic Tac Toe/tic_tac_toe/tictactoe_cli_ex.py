from random import randrange

# static game data - doesn't change (hence immutable tuple data type)
WIN_SET = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
           (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))

# global variables for game data
board = [' '] * 9
current_player = ''  # 'x' or 'o' for first and second player
ai_choices = {'r': 'Random', 'a': 'Average Ai', 's': 'Smart AI'}
ai_choice = None
ai_vs_ai = False
players = {'x': 'Human', 'o': 'Super AI'}
winner = None
move = None
firstTurn = True
quitting = False

# aesthetics...
HR = '-' * 40


#==============================================================================
# Game model functions

def reset_game_data():
    '''Resets the game data in the global variables to the defaults'''
    global board, current_player, ai_choice, ai_choices, ai_vs_ai, players, winner, move, firstTurn, quitting
    board = [' '] * 9
    current_player = ''  # 'x' or 'o' for first and second player
    ai_choices = {'r': 'Random', 'a': 'Average Ai', 's': 'Smart AI'}
    ai_choice = None
    ai_vs_ai = False
    players = {'x': 'Human', 'o': 'Super AI'}
    winner = None
    move = None
    firstTurn = True
    quitting = False


def check_move():
    '''This function will return True if ``move`` is valid (in the board range 
    and free cell), or print an error message and return False if not valid. 
    ``move`` is an int board position [0..8].
    '''
    global move
    try:
        move = int(move)
        if board[move] == ' ':
            return True
        else:
            print('>> Sorry - that position is already taken!')
            return False
    except:
        print('>> %s is not a valid position! Must be int between 0 and 8.' % move)
        return False


def check_set_for_player(set, player):

    count = 0
    move = -1

    for x, index in enumerate(set):
        if board[index] == player:
            count += 1
        elif board[index] != 'x' and board[index] != 'o':
            move = index
            if x == 2 and count != 2:
                # if the count is at two when we have ennumerated through the set then we set move
                # to -1 to indicate to return false
                move = -1
        else:
            move = -1

    return move


def check_for_result():
    '''Checks the current board to see if there is a winner, tie or not.
    Returns a 'x' or 'o' to indicate a winner, 'tie' for a stale-mate game, or
    simply False if the game is still going.
    '''
    for row in WIN_SET:
        if board[row[0]] == board[row[1]] == board[row[2]] != ' ':
            return board[row[0]]  # return an 'x' or 'o' to indicate winner

    if ' ' not in board:
        return 'tie'

    return None


#==============================================================================
# agent (human or AI) functions


def get_human_move():
    '''Get a human players raw input. Returns None if a number is not entered.'''
    return input('[0-8] >> ')


def get_ai_move():
    '''Get the AI's next move '''
    # A simple dumb random move - valid or NOT!
    # Note: It is the models responsibility to check for valid moves...
    return randrange(9)  # [0..8]


def get_average_ai_move():

    global current_player

    if current_player == 'x':
        otherPlayer = 'o'
    else:
        otherPlayer = 'x'

    for set in WIN_SET:
        # Check if other player is about to win using check_set().
        chk = check_set_for_player(set, otherPlayer)
        if chk != -1:
            return chk
        # Then make the move to stop the other player from winning
    #else choose a random option
    return randrange(9)  # [0..8]


def get_smart_ai_move():


    global current_player, firstTurn

    if current_player == 'x':
        otherPlayer = 'o'
    else:
        otherPlayer = 'x'

    for set in WIN_SET:
        # Check if this player is about to win using check_set()
        chk = check_set_for_player(set, current_player)
        if chk != -1:
            return chk
        # Then make the move that allows you to win
    # Check if other player is about to win using check_set().
        chk = check_set_for_player(set, otherPlayer)
        if chk != -1:
            return chk
        # Then make the move to stop the other player from winning

    # if its the first turn, return the middle
    if firstTurn:
        firstTurn = False  # set this to False so it only tries this once.
        return 4

    # If neither condition
    # Then make a random move from available spaces
    return randrange(9)  # [0..8]


#==============================================================================
# Standard trinity of game loop methods (functions)

def process_input():
    '''Get the current players next move.'''
    # save the next move into a global variable
    global move, ai_choice
    if current_player == 'x':
        move = get_human_move()
    elif ai_choice == 's':
        move = get_smart_ai_move()
    elif ai_choice == 'a':
        move = get_average_ai_move()
    elif ai_choice == 'r':
        move = get_ai_move()
    else:
        move = get_ai_move()  # Defaults to the random AI


def process_ai_vs_ai_input():
    '''Get the current players next move, where there are two ai battling.'''
    # save the next move into a global variable
    global move, ai_choice
    if current_player == 'x':
        move = get_smart_ai_move()  # Always Smart AI vs another AI
    elif ai_choice == 's':
        move = get_smart_ai_move()
    elif ai_choice == 'a':
        move = get_average_ai_move()
    elif ai_choice == 'r':
        move = get_ai_move()
    else:
        move = get_ai_move()  # Defaults to the random AI


def update_model():
    '''If the current players input is a valid move, update the board and check 
    the game model for a winning player. If the game is still going, change the
    current player and continue. If the input was not valid, let the player
    have another go.
    '''
    global winner, current_player

    if check_move():
        # do the new move (which is stored in the global 'move' variable)
        board[move] = current_player
        # check board for winner (now that it's been updated)
        winner = check_for_result()
        # change the current player (regardless of the outcome)
        if current_player == 'x':
            current_player = 'o'
        else:
            current_player = 'x'
    else:
        print('Try again')


def render_board():
    '''Display the current game board to screen.'''

    print('    %s | %s | %s' % tuple(board[:3]))
    print('   -----------')
    print('    %s | %s | %s' % tuple(board[3:6]))
    print('   -----------')
    print('    %s | %s | %s' % tuple(board[6:]))

    # pretty print the current player name
    if winner is None:
        print('The current player is: %s' % players[current_player])

#==============================================================================


def show_human_help():
    '''Show the player help/instructions. '''
    tmp = '''
To make a move enter a number between 0 - 8 and press enter.  
The number corresponds to a board position as illustrated:
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
    '''
    print(tmp)
    print(HR)


def run_human_vs_ai_game():
    '''Run a Human Vs AI game'''
    show_human_help()

    # by default the human player starts. This could be random or a choice.
    global current_player
    current_player = 'x'

    # show the initial board and the current player's move
    render_board()

    # Standard game loop structure
    while winner is None:
        process_input()
        update_model()
        render_board()


def run_ai_vs_ai_game():
    '''Run a game between a Smart AI and a selected AI'''
    # by default 'x' starts
    global current_player
    current_player = 'x'

    # Standard game loop structure
    while winner is None:
        process_ai_vs_ai_input()
        update_model()

    # Render the Final Board State
    render_board()


#==============================================================================
# Separate the running of the game using a __name__ test. Allows the use of this
# file as an imported module
#==============================================================================
if __name__ == '__main__':
    # Welcome ...
    print('Welcome to the amazing+awesome tic-tac-toe! \n')
    while not quitting:
        # Choose to play or have the AI fight it out
        print('Do you want the smart AI to fight on your behalf?')
        choice = input ('[Y/N] -> ')
        if choice == 'Y' or choice == 'y':
            ai_vs_ai = True
        else:
            ai_vs_ai = False

        # Select the AI opponent playing second
        print('\nSelect the opponent')
        for key in ai_choices.keys():
            print(key, ai_choices[key])
        ai_choice = input('>> ')

        if ai_vs_ai:
            run_ai_vs_ai_game()
        else:
            run_human_vs_ai_game()

        # Some pretty messages for the result
        print(HR)
        if winner == 'tie':
            print('TIE!')
        elif winner in players:
            print('%s is the WINNER!!!' % players[winner])
        print(HR)
        print('Play Again?')
        tmp = input('[Y/N] -> ')
        if tmp == 'Y' or tmp == 'y':
            reset_game_data()

        else:
            quitting = True
            print('Goodbye, Thank you for playing.')

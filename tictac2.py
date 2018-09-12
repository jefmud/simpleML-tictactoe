import random
# here are the traditional game tokens... blank, X and O
tokens = [' ','X','O']


class Board:
    """representation of a Tic Tac Toe board object"""
    def __init__(self):
        self.board = None
        self.clear()
    
    def clear(self):
        """initialize the board and fill it with blanks (tokens[0])"""
        self.board = []
        for _ in range(0,3):
            self.board.append([tokens[0], tokens[0], tokens[0]])

    def move(self, player, row, col):
        """make a single move on the board, return True if valid False if not"""
        # if a token is NOT present
        if self.board[row][col] == tokens[0]:
            self.board[row][col] = player
            return True
        return False

    @staticmethod
    def next_token(token):
        """return next player token, give current token"""
        if token == tokens[1]:
            return tokens[2]
        return tokens[1]

    def is_winner(self, token):
        """return True if this token is a winner, else return False"""
        winning_ranks = [
            [(0,0), (0,1), (0,2)],  # row winner
            [(1,0), (1,1), (1,2)],
            [(2,0), (2,1), (2,2)],
            [(0,0), (1,0), (2,0)],  # column winner
            [(0,1), (1,1), (2,1)],
            [(0,2), (1,2), (2,2)],
            [(0,0), (1,1), (2,2)],  # diagonal winner
            [(0,2), (1,1), (2,0)]
        ]

        # check if the token completely fills ANY of the winning ranks
        for wr in winning_ranks:
            i_win = True
            for p in wr:
                if self.board[p[0]][p[1]] != token:
                    i_win = False
            if i_win:
                return True

    @property
    def winner(self):
        """return winning token or None"""
        for token in [tokens[1], tokens[2]]:
            if self.is_winner(token):
                return token
        return None

    @property         
    def draw(self):
        """return a draw when board serial has no zeros"""
        ss = self.serial
        if '0' in ss:
            return False
        return True

    def show(self):
        """display a board onscreen"""
        print('-'*5)
        for row in range(0,3):
            print('{}|{}|{}'.format(self.board[row][0], self.board[row][1], self.board[row][2]))
            print('-'*5)
            
    @property
    def serial(self):
        """return a "serial" of the board state
        first three digits is first row, second three digits is second row, etc.
        0 = blank token, 1 = X, 2 = O
        000000000 = blank board
        100000000 = X in the first row and column
        100200000 = X in first row and column, O in second row first column
        """
        s_serial = []
        for row in range(0,3):
            for col in range(0,3):
                s_serial.append(str(tokens.index(self.board[row][col])))
        return ''.join(s_serial)
                
    def serial2board(self, ser):
        """convert a board serial string representation into board array representation"""
        self.clear()
        row = 0
        col = 0
        for ch in ser:
            self.board[row][col] = tokens[int(ch)]
            col += 1
            if col > 2:
                row += 1
                col=0

    def index2rowcol(self, index):
        """return a row, col from a serial index"""
        current_index = 0
        for row in range(0,3):
            for col in range(0,3):
                if current_index == index:
                    return row, col
                current_index += 1
        raise OverflowError

    def move_from_serials(self, serial1, serial2):
        """return a move tuple to show how serial1 will change to serial2"""
        indices = []
        for index in range(0, len(serial1)):
            if serial1[index] != serial2[index]:
                indices.append(index)
        if len(indices) > 1:
            raise OverflowError
        index = indices[0]
        row, col = self.index2rowcol(index)
        player = tokens[int(serial2[index])]
        return (player, row, col)


    def random_move(self, player):
        """make a random move for the player, return tuple of move row and column"""
        valid_move = False
        iterator = 0
        while not valid_move:
            row = random.randint(0, 2)
            col = random.randint(0, 2)
            iterator += 1
            if self.move(player, row, col):
                valid_move = True
            if iterator > 100:
                # protection from infinite loop
                raise OverflowError
        return (player, row, col)

    def random_board(self, turns, player=None):
        """obsolete due to game object with simulate"""
        # plays a game with a specific number of turns, starting player

        if player is None:
            # choose a random player
            player = random.choice([tokens[1],tokens[2]])
        if turns >= 9:
                turns = 9

        for _ in range(0,turns):
            valid_move = False
            iterations = 0 # used to protect against infinite loops
            while not valid_move:
                # keep trying random combinations until we can make a valid move
                row = random.randint(0, 2)
                col = random.randint(0, 2)
                if self.move(player, row, col):
                    iterations = 0
                    valid_move = True
                    player = self.next_token(player)
                else:
                    iterations += 1
                if iterations > 100:
                    # looks like an infinite loop, throw error
                    raise OverflowError

        return self.serial


class Game:
    """a game object, use simulate to run a game"""
    # play a game
    moves = []
    board_serials = []
    winner = None

    def __init__(self):
        self.clear()

    def clear(self):
        self.moves = []
        self.board_serials = []
        self.winner = None
    
    def random_to_win(self, player=None):
        """play a random game until player wins - used to develop a training set"""
        moves = []
        b = Board() # create a local board
        self.board_serials.append(b.serial)
        if player is None:
            player = random.choice([tokens[1],tokens[2]])

        while True:
            row = random.randint(0,2)
            col = random.randint(0,2)
            if b.move(player, row, col):
                moves.append((row,col,player))
                self.board_serials.append(b.serial)
                player = b.next_token(player)

            # check for a winner
            winner = b.winner
            if winner:
                self.moves = moves
                self.winner = winner
                return b.serial, moves

            # check for a draw
            if b.draw:
                moves = []
                b.clear()

    def human_input(self, player, board):
        """get human input from console"""
        while True:
            board.show()
            this_move = input("Enter a move as row, col for {}: ".format(player))
            try:
                rc = this_move.split(',')
                row = int(rc[0])
                col = int(rc[1])
                if board.board[row][col] == tokens[0]:
                    return (player, row, col)
            except Exception as e:
                print(e)
            print("That was an invalid move for {}".format(player))
            
    def trained(self, first_player, player, board, training):
        """attempt to make an informed move based on the training set"""
        # get training which matches a player
        player_training = training.get(player, [])

        # find possible moves from current player training set
        possible_moves = []
        for example in player_training:
            try:
                # find the index of the example
                p = example.index(board.serial)

                # find the next serial in the sequence
                next_serial = example[p+1]

                # find out how to move to satisfy next_serial in sequence
                possible_move = board.move_from_serials(board.serial, next_serial)

                # if the move matches the player, put it in the list of possible moves
                if possible_move[0] == player:
                    possible_moves.append(possible_move)
            except:
                # the current board.serial is not in this example, ignore error
                pass

        # if there is at least one possible move, return the first one.
        # rationale, it is on the shortest line to a win because of the way we build the training set
        if len(possible_moves) > 0:
            return possible_moves[0]

        return board.random_move(player)

    def simulate(self, first_player=None, training=None, human_player=False):
        """simulate(first_move_tokensimulate a game, return the winner. 
        first_player=token (e.g. X,O) of who makes first move
        training = a training set
        """
        board = Board()

        if first_player is None:
            current_player = random.choice([tokens[1],tokens[2]])
            first_player = current_player
        else:
            current_player = first_player

        # initialize board serials and moves
        self.board_serials = [board.serial]  # start with empty board
        self.moves = []  # recorded moves

        while board.winner is None and board.draw is False:
            # while no winner or draw
            if human_player == current_player:
                # handle human player
                this_move = self.human_input(human_player, board)
                board.move(human_player,this_move[1],this_move[2])
            else:
                # handle random move
                if training is None:
                    this_move = board.random_move(current_player)
                else:
                    this_move = self.trained(first_player=first_player, player=current_player, board=board, training=training)
                    board.move(current_player, this_move[1], this_move[2])

            self.moves.append(this_move)
            self.board_serials.append(board.serial)
            current_player = board.next_token(current_player)

        return board.winner



def test1():
    """a first run to see what a training set might look like"""
    board = Board()
    training_set = {} # a dictionary of end 0f game serials mapped to winning token
    while True:
        board.clear()
        board.random_board(5)
        board.show()
        winner = board.winner
        print("winner=" + str(winner))
        print("serial=" + board.serial)
        if winner:
            training_set[board.serial] = winner
            board.serial2board(board.serial)
            board.show()
            print(len(training_set))
            x = input("Hit ENTER to continue")    


def test2():
    """run a random game to win, recording all moves and extracting serials"""
    b = Board()
    game = Game()
    ser, moves = game.random_to_win()
    print(ser)
    print(moves)
    b.serial2board(ser)
    b.show()
    print('winner=' + game.winner)
    print(game.board_serials)


def test3():
    # learn something
    player = 'X'
    # do 50 games
    game = Game()
    training = []
    training_count = 50
    print("training on %s games" % (training_count))
    for _ in range(0, training_count):
        game.random_to_win(player)
        training.append(game.board_serials)
        game.clear()
    print("training complete")
    simulated_games = 1000
    wins = 0
    losses = 0
    draws = 0
    for _ in range(0, simulated_games):
        # play game
        #winner = game.simulate(player=player, first_move=player, training=training)
        #winner = game.simulate(first_player=player)
        winner = game.simulate()
        if winner is None:
            draws += 1
        else:
            if winner == player:
                wins += 1
            else:
                losses += 1
    print("Simulation of {} games".format(simulated_games))
    print("wins={} losses={} draws={}".format(wins, losses, draws))



def test4():
    """simulate a game"""
    game = Game()
    result = game.simulate(human_player='X')
    print('winner is {}'.format(result))
    print('game serials: {}'.format(game.board_serials))
    print('game moves: {}'.format(game.moves))


def test5():
    """send some training data to the simulation"""
    game = Game()
    training_set = {}
    training_count = 1000
    length = 7
    player = 'X' # testing player X
    for length in range(6,10):
        for _ in range(0, training_count):
            winner = game.simulate()
            if winner:
                if len(game.board_serials) < length:
                    winner_training = training_set.get(winner)
                    if winner_training is None:
                        winner_training = []
                    winner_training.append(game.board_serials)
                    if winner==player:
                        # see if the training actually helps the particular player!
                        training_set[winner] = winner_training
    print("training completed with {} samples".format(len(training_set[player])))

    simulated_games = 1000
    wins = 0
    losses = 0
    draws = 0
    human_player=None
    for _ in range(0, simulated_games):
        # play game
        winner = game.simulate(first_player=player, training=training_set, human_player=human_player)
        if winner is None:
            draws += 1
            if human_player:
                print('You draw')
        else:
            if winner == player:
                wins += 1
                if human_player:
                    print('Human loses')
            else:
                if human_player:
                    print('Human wins')
                losses += 1
    print("Simulation of {} games".format(simulated_games))
    print("wins={} losses={} draws={}".format(wins, losses, draws))


if __name__ == '__main__':
    test5()
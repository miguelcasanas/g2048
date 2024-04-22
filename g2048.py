import curses as cr
from time import sleep
import numpy as np
import os

class Game:
    def __init__(self, L):
        self.size = L
        self.score = 0
        self.board = np.zeros((L, L), dtype=int)
        while np.sum(self.board) < 4:
            x, y = np.random.randint(L, size=(2,))
            self.board[x, y] = 2
        self.old_board = self.board.copy()
        self.best_path = ".g2048_best"
        if os.path.exists(self.best_path):
            with open(self.best_path, 'r') as f:
                self.best = int(f.read())
        else:
            self.best = 0
    
    def __str__(self) -> str:
        L, board = self.size, self.board
        widths = [len(str(max(board[:, col]))) for col in range(L)]
        table = ""
        for i in range(L):
            for j in range(L):
                table += f"{board[i, j]:{widths[j]+1}}"
            if i < L:
                table += '\n'
        return table

    def move_row(self, row):
        def remove_zeros():
            for i in range(1, self.size):
                j = i
                while row[j-1] == 0 and j > 0:
                    row[j-1] = row[j]
                    row[j] = 0
                    j -= 1
        remove_zeros()
        for i in range(1, self.size):
            if row[i-1] == row[i]:
                row[i-1] *= 2
                self.score += row[i-1]
                if self.score > self.best:
                    self.best = self.score
                row[i] = 0
        remove_zeros()
        return row
    
    def move_all(self, board):
        for row in board:
            row = self.move_row(row)
        return board
    
    def move(self, dir):
        self.old_board = self.board.copy()
        if dir == 'l':
            self.board = self.move_all(self.board)
        elif dir == 'r':
            self.board = self.move_all(self.board[:,::-1])[:,::-1]
        elif dir == 'u':
            self.board = self.move_all(self.board.T).T
        else:
            self.board = self.move_all(self.board.T[:,::-1])[:,::-1].T
    
    def add_one(self):
        while True:
            x, y = np.random.randint(self.size, size=(2,))
            if self.board[x, y] == 0:
                self.board[x, y] = 2 if np.random.random() > 0.2 else 4
                break

    def move_is_possible(self):
        return not np.all(self.board == self.old_board)

    def won(self):
        return np.max(self.board) == 2048
    
    def lost(self):
        if np.any(self.board == 0):
            return False
        pairs = []
        L = self.size
        for i in range(L):
            for j in range(L):
                if j > 0:
                    pairs.append(self.board[i,j-1:j+1])
                if i > 0:
                    pairs.append(self.board[i-1:i+1,j])
        return all(p[0] != p[1] for p in pairs)
    
    def play_again(self):
        with open(self.best_path, 'w') as f:
            f.write(str(self.best))
        self.clear_buffer()
        return True if self.screen.getkey() == 'y' else False

    def set_screen(self, screen):
        self.screen = screen
        cr.init_pair(1, cr.COLOR_WHITE, cr.COLOR_BLACK)
        cr.init_pair(2, cr.COLOR_RED, cr.COLOR_BLACK)
        cr.init_pair(3, cr.COLOR_CYAN, cr.COLOR_BLACK)
        cr.init_pair(4, cr.COLOR_GREEN, cr.COLOR_BLACK)
        screen.clear()
    
    def clear_buffer(self):
        self.screen.nodelay(True)
        while self.screen.getch() != -1:
            pass
        self.screen.nodelay(False)

    def get_key(self):
        key = self.screen.getch()
        if key == cr.KEY_UP:
            self.move('u')
        elif key == cr.KEY_DOWN:
            self.move('d')
        elif key == cr.KEY_LEFT:
            self.move('l')
        elif key == cr.KEY_RIGHT:
            self.move('r')
        elif key == ord('q'):
            return 'q'
        else:
            return key

    def print_line(self, y, x, txt, t, c):
        self.screen.addstr(y, x, ' ' * 24)
        self.screen.addstr(y, x, txt, cr.color_pair(c))
        self.screen.refresh()
        if t:
            sleep(t)
            self.screen.addstr(y, x, ' ' * len(txt))
            self.screen.refresh()
    
    def print_title(self):
        title = [' ___ ___ ___ ___ ', '|_  |   | | | . |', '|  _| | |_  | . |', '|___|___| |_|___|']
        for i in range(len(title)):
            self.print_line(i, 5, title[i], 0, 4)
            sleep(0.2)
    
    def print_instructions(self):
        self.print_line(5, 5, "Press ◀ ▲ ▼ ▶ to move.", 1.5, 1)
        self.print_line(5, 5, " " * 20, 0.5, 1)
        self.print_line(5, 5, "Press 'q' to quit.", 1.5, 1)

    def print_board(self):
        raw_board = str(self)
        width = raw_board.find('\n') + 1
        left = 8
        framed_board = ['╭' + '─' * width + '╮\n']
        lines = raw_board.splitlines()
        for line in lines:
            framed_board += ['│' + line.replace('0', '▯') + ' │\n']
        framed_board += ['╰' + '─' * width + '╯']

        for i in range(len(framed_board)):
            self.print_line(5 + i, 5, framed_board[i], 0, 1)

        self.print_line(12, 5, f"Score: {self.score}", 0, 3)
        self.print_line(13, 5, f"Best: {self.best}", 0, 3)

def main(stdscr):
    cr.curs_set(False)

    game = Game(4)
    game.set_screen(stdscr)
    game.print_title()
    game.print_instructions()
    game.print_board()
    game.clear_buffer()

    while True:
        key = game.get_key()
        if key == 'q':
            break
        elif key:
            continue
    
        if not game.move_is_possible():
            game.print_line(11, 5, "Not allowed!", 0.4, 2)
            continue

        game.add_one()
        game.print_board()

        if game.won():
            game.print_line(11, 5, "You WON!", 2, 4)
            game.print_line(15, 5, "Play again? 'y' for yes.", 0, 1)
            if game.play_again():
                game.print_line(15, 5, 24 * ' ', 0, 1)
                game.__init__(4)
                game.print_board()
            else:
                break

        if game.lost():
            game.print_line(11, 5, "You LOST!", 2, 2)
            game.print_line(15, 5, "Play again? 'y' for yes.", 0, 1)
            if game.play_again():
                game.print_line(15, 5, 24 * ' ', 0, 1)
                game.__init__(4)
                game.print_board()
            else:
                break
        
cr.wrapper(main)
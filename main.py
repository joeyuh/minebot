import pyautogui
import time
import numpy as np
import pynput
from PIL.Image import Image
from numpy.core._multiarray_umath import ndarray
from pynput.mouse import Button, Controller
from PIL import Image, ImageGrab


class GameBoard:
    board: ndarray

    def __init__(self, height: int = 16, width: int = 30, init: bool = False, downscale: float = 1.0):
        self.COLOR_MAP = {
            (189, 189, 189, 255): 0,
            (0, 35, 245, 255): 1,
            (53, 120, 32, 255): 2,
            (235, 50, 35, 255): 3,
            (0, 11, 118, 255): 4,
            (112, 19, 11, 255): 5,
            (52, 121, 122, 255): 6,
            (142, 142, 142, 255): 7,
            (123, 123, 123, 255): 8,
        }
        self.MOVE_MAP = [
            [1, 0],
            [0, 1],
            [1, 1],
            [-1, 0],
            [0, -1],
            [-1, -1],
            [-1, 1],
            [1, -1],
        ]
        self.GAME_HEIGHT = height  # y
        self.GAME_WIDTH = width   # x
        self.SMILE_COORD = 227, 0
        self.TOP_LEFT = 0, 39
        self.downscale = downscale
        if init:
            self.locate_game_screen()
        # 0: Unchecked, 1 - 8: Number of mines around, -2: Checked: No mine, -1 Flagged
        self.board = np.zeros((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.mouse = pynput.mouse.Controller
        self.screenshot = Image.new('RGB', pyautogui.size()).load()
        self.movable = []  # Checked field that could contain useful clue
        self.moved = set()  # Checked field in which the clues are already used

    def calculate_scale(self):
        """
        Experimental: calculate display scaling by taking the dimensions of a screenshot and compare to pyautogui
        :return: calculated scale
        """
        self.downscale = ImageGrab.grab().width / pyautogui.size().width
        return self.downscale

    def locate_game_screen(self, seconds: int = 3, confidence: float = 0.9):
        """
        Locate the http://minesweeperonline.com game screen (Perhaps the Windows XP one too!)

        :param seconds: Number of seconds to wait before checking
        :param confidence: pyautogui locateOnScreen confidence
        :return: pair of int
        """
        res = 0, 0
        time.sleep(seconds)
        try:
            res = pyautogui.locateOnScreen('smile.png', confidence=confidence)
            self.SMILE_COORD = res[0] / self.downscale + 10, res[1] / self.downscale + 10
            self.TOP_LEFT = res[0] / self.downscale - 226, res[1] / self.downscale + 40

        except TypeError:
            print(f"Image Not Found, retrying in {seconds} seconds!")
            self.locate_game_screen(seconds, confidence)

        return res

    def return_center(self, x: int, y: int):
        return self.TOP_LEFT[0] + 16 * x + 8, self.TOP_LEFT[1] + 16 * y + 8

    def refresh(self):
        print("Refresh")
        # start_time = time.time()
        self.movable.clear()
        self.screenshot = ImageGrab.grab().load()
        # print(self.screenshot.size)
        for x in range(self.GAME_WIDTH):
            for y in range(self.GAME_HEIGHT):
                if self.board[x][y] == -1:
                    continue  # if we already labeled it as mine, skip
                a, b = self.return_center(x, y)
                color = self.screenshot[(a - 8) * self.downscale, (b - 8) * self.downscale]  # check top left corner
                if color == (255, 255, 255, 255):  # if it's white
                    self.board[x][y] = -2  # we mark as unchecked
                    continue
                color = self.screenshot[a * self.downscale, b * self.downscale]  # check center
                # print(self.COLOR_MAP[color])
                self.board[x][y] = self.COLOR_MAP[color]  # fill in by color table
                if self.board[x][y] > 0 and (x, y) not in self.moved:
                    # print((x,y))
                    self.movable.append((x, y))

        # print(self.board)

        # print("--- %s seconds ---" % (time.time() - start_time))

    def solve(self):
        for times in range(200):
            # print(f'Size {len(self.movable)}')
            for field in self.movable:
                x, y = field
                if self.move(x, y):
                    self.refresh()
                    break

    def move(self, x: int, y: int) -> bool:
        res = False  # Record if we did anything
        number = self.board[x][y]
        unchecked = 0
        uncheckeds = []
        flagged = 0
        # flaggeds = []
        for moves in self.MOVE_MAP:
            dx, dy = moves
            xx = x + dx
            yy = y + dy
            if 0 <= xx < self.GAME_WIDTH and 0 <= yy < self.GAME_HEIGHT:  # check bounds
                checking = self.board[xx][yy]
                if checking == -1:
                    flagged += 1
                    # flaggeds.append((xx,yy))
                if checking == -2:
                    unchecked += 1
                    uncheckeds.append((xx,yy))

        mouse=Controller()
        mouse.position = self.TOP_LEFT
        print(f'Num {number}, Unchecked {unchecked}, flagged {flagged}')
        if unchecked + flagged == number:  # all mine confirmed, flagging all
            for field in uncheckeds:
                print("Flagging")
                xx, yy = field
                self.board[xx][yy] = -1
                unchecked -= 1
                time.sleep(0.01)
                self.click(xx, yy, Button.right)  # Right click, mine found
                res = True

        if flagged == number:  # all mine already flagged, left clicking all
            for field in uncheckeds:
                print("Checking")
                xx, yy = field
                time.sleep(0.01)
                self.click(xx, yy, Button.left)  # Left click, no mine
                res = True
        elif flagged > number:  # Impossible, something went wrong
            raise Exception('Game Logics Critical Error')

        if res:
            self.moved.add((x,y))

        return res

    def click(self, x: int, y: int, button=Button.left):
        mouse = Controller()
        mouse.position = (self.return_center(x, y))
        time.sleep(0.01)
        mouse.press(button)
        mouse.release(button)


if __name__ == "__main__":
    print(pyautogui.size())
    print(ImageGrab.grab().size)
    game = GameBoard()
    print(game.calculate_scale())
    game.locate_game_screen(3, 0.5)
    # time.sleep(0.5)
    # pyautogui.click(game.SMILE_COORD)
    # time.sleep(0.5)
    # pyautogui.click(game.TOP_LEFT[0]+8,game.TOP_LEFT[1]+8)
    mouse = Controller()
    game.refresh()
    game.solve()
    print()

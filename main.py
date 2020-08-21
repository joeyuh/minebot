import pyautogui
import time
import numpy as np
import pynput
from PIL.Image import Image
from pynput.mouse import Button, Controller
from PIL import Image, ImageGrab


class GameBoard:

    def __init__(self, width: int = 30, length: int = 16, init: bool = False, downscale: float = 1.0):
        self.GAME_WIDTH = width
        self.GAME_LENGTH = length
        self.SMILE_COORD = 227, 0
        self.TOP_LEFT = 0, 39
        self.downscale = downscale
        if init:
            self.locate_game_screen()
        # 0: Unchecked, 1 - 8: Number of mines around, -1: Checked: No mine, -2
        self.board = np.zeros((self.GAME_WIDTH, self.GAME_LENGTH))
        self.mouse = pynput.mouse.Controller
        self.screenshot = Image.new('RGB', pyautogui.size()).load()

    def locate_game_screen(self, seconds: int = 3, confidence: float = 1.0):
        """
        Locate the http://minesweeperonline.com game screen (Perhaps the Windows XP one too!)

        :param seconds: Number of seconds to wait before checking
        :param confidence: pyautogui locateOnScreen confidence
        :param downscale: divide the coords returned locateOnScreen by this number
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
        self.screenshot = ImageGrab.grab().load()
        # print(self.screenshot.size)

        for x in range(self.GAME_WIDTH):
            for y in range(self.GAME_LENGTH):
                a, b = self.return_center(x, y)
                color = self.screenshot[a*self.downscale, b*self.downscale]
                self.click(a, b)
                print(color)

    def solve(self):
        pass

    def move(self):
        pass

    def click(self, x: int = 0, y: int = 0):
        mouse = Controller()
        mouse.position = (self.return_center(x, y))
        # mouse.press(Button.left)
        # mouse.release(Button.left)


if __name__ == "__main__":
    print(pyautogui.size())
    print(ImageGrab.grab().size)
    game = GameBoard(downscale=2)
    game.locate_game_screen(3, 0.5)
    # time.sleep(0.5)
    # pyautogui.click(game.SMILE_COORD)
    # time.sleep(0.5)
    # pyautogui.click(game.TOP_LEFT[0]+8,game.TOP_LEFT[1]+8)
    mouse = Controller()
    game.refresh()

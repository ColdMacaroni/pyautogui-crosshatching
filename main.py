import pyautogui
from time import sleep
from PIL import Image
from sys import argv

VALUES = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}

class Pixel:
    SIZE = 5

    def __init__(self, value):
        if value in VALUES:
            self.value = value
        else:
            raise ValueError(f"Value must be within {VALUES}")

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value}>"

    def draw(self, x, y):
        # these are cumulative, which is why im using disconnected if statements.
        # On another language i'd use cascading cases in a switch
        d=0

        # With a value of 0 we dont do anything.

        # Single diagonal
        if self.value >= 1:
            # Go to the bottom left of the square
            pyautogui.moveTo(x, y + self.SIZE, duration=d)

            # Draw a bl tr diagonal
            pyautogui.drag(self.SIZE, -self.SIZE, duration=d)

        # Draw two diagonals
        if self.value >= 2:
            # Go to the left, 1/2 down of the square
            pyautogui.moveTo(x, y + self.SIZE/2)

            # Draw the top diagonal
            pyautogui.drag(self.SIZE/2, -self.SIZE/2, duration=d)

            # go to middle bottom
            pyautogui.moveTo(x + self.SIZE/2, y + self.SIZE)

            # Draw the bottom diagonal
            pyautogui.drag(self.SIZE/2, -self.SIZE/2, duration=d)

        # Single diagonal, other way
        if self.value >= 3:
            # Go to the top left of the square
            pyautogui.moveTo(x, y)

            # Draw a tl br diagonal
            pyautogui.drag(self.SIZE, self.SIZE, duration=d)

        # Draw two diagonals, other way
        if self.value >= 4:
            # Go to 1/2 right of the square
            pyautogui.moveTo(x + self.SIZE/2, y)

            # Draw the top diagonal
            pyautogui.drag(self.SIZE/2, self.SIZE/2, duration=d)

            # go to middle bottom
            pyautogui.moveTo(x, y + self.SIZE/2)

            # Draw the bottom diagonal
            pyautogui.drag(self.SIZE/2, self.SIZE/2, duration=d)

        # Single vertical line
        if self.value >= 5:
            # Top middle
            pyautogui.moveTo(x + self.SIZE/2, y)

            # Draw to bottom middle
            pyautogui.drag(0, self.SIZE, duration=d)

        # two vertical lines
        if self.value >= 6:
            # Bottom 1/4 from left
            pyautogui.moveTo(x + self.SIZE/4, y + self.SIZE)

            # Draw to top 1/4 from left
            pyautogui.drag(0, -self.SIZE, duration=d)

            # Top 3/4 from left
            pyautogui.moveTo(x + self.SIZE * 3/4, y)

            # Draw to bottom 3/4 from left
            pyautogui.drag(0, self.SIZE, duration=d)

        # Single horizontal line
        if self.value >= 7:
            # right middle
            pyautogui.moveTo(x + self.SIZE, y + self.SIZE/2)

            # Draw to left middle
            pyautogui.drag(-self.SIZE, 0, duration=d)

        # two vertical lines
        if self.value >= 8:
            # left 1/4 from top
            pyautogui.moveTo(x, y + self.SIZE/4)

            # Draw to right 1/4 from top
            pyautogui.drag(self.SIZE, 0, duration=d)

            # left 3/4 from top
            pyautogui.moveTo(x, y + self.SIZE * 3/4)

            # Draw to right 3/4 from top
            pyautogui.drag(self.SIZE, 0, duration=d)

        # if self.value >= 9:
        #     # This will completely fill the square
        #     # Move to start
        #     pyautogui.moveTo(x, y)
        #     # Fill EVERYTHING
        #     for i in range(self.SIZE + 1):
        #         if i % 2:  # odd
        #             # Go left
        #             pyautogui.drag(-self.SIZE, 0)

        #         else: # even
        #             # Go right
        #             pyautogui.drag(self.SIZE, 0)

        #         # Go down one to move onto the next row
        #         pyautogui.move(0, 1)
        if self.value >= 9:
            # Draw box around
            pyautogui.moveTo(x, y)
            pyautogui.drag(self.SIZE, 0, duration=d)
            pyautogui.drag(0, self.SIZE, duration=d)
            pyautogui.drag(-self.SIZE, 0, duration=d)
            pyautogui.drag(0, -self.SIZE, duration=d)


def matrix_to_pixels(ls: list[list[int]]):
    matrix = []

    for y in range(len(ls)):
        matrix.append(list())
        for x in range(len(ls[y])):
            matrix[y].append(Pixel(ls[y][x]))

    return matrix

def read_file(fn: str):
    img = Image.open(fn)

    # convert to black and white
    bw_img = img.convert('L')

    width, height = bw_img.size
    matrix = list()
    for y in range(height):
        matrix.append(list())
        for x in range(width):
            # Clamp between values
            matrix[-1].append(round((255 - bw_img.getpixel((x, y))) / 255 * 9))
            print(f"{matrix[-1][-1]} ", end="")
        print()

    return matrix

def main():
    # test = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
    #         [1, 2, 3, 4, 5, 6, 7, 8, 9],
    #         [2, 3, 4, 5, 6, 7, 8, 9, 8],
    #         [3, 4, 5, 6, 7, 8, 9, 8, 7],
    #         [4, 5, 6, 7, 8, 9, 8, 7, 7]]
    test = []
    for i in range(0, 10):
        test.append([])
        for x in range(0, 10):
            test[-1].append((i - x) % 10)

    pixel_matrix = matrix_to_pixels(read_file(argv[1]))
    # pixel_matrix = matrix_to_pixels(test)

    sleep(1)
    og_x, og_y = pyautogui.position()

    # draw em
    for y in range(len(pixel_matrix)):
        for x in range(len(pixel_matrix[y])):
            pixel_matrix[y][x].draw(og_x + Pixel.SIZE * x, og_y + Pixel.SIZE * y)


if __name__ == "__main__":
    main()

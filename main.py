import pyautogui
from time import sleep


VALUES = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}

class Pixel:
    SIZE = 10

    def __init__(self, value):
        if value in VALUES:
            self.value = value
        else:
            raise ValueError(f"Value must be within {VALUES}")

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value}>"

def matrix_to_pixels(ls: list[list[int]]):
    matrix = []

    for y in range(len(ls)):
        matrix.append(list())
        for x in range(len(ls[y])):
            matrix[y].append(Pixel(ls[y][x]))

    return matrix

def main():
    test = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [2, 3, 4, 5, 6, 7, 8, 9, 0],
            [3, 4, 5, 6, 7, 8, 9, 0, 0],
            [4, 5, 6, 7, 8, 9, 0, 0, 0]]

    pixel_matrix = matrix_to_pixels(test)

if __name__ == "__main__":
    main()

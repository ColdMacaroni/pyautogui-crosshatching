import pyautogui
from time import sleep
from PIL import Image
from sys import argv

# How dark the image is
VALUES = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}

# Value lines, each one also includes the ones below
# 0 - Nothing
# 1 - One line, /
# 2 - Two lines, a / starting at half the left side
#                another starting at half the bottom side
# 3 - One line, \
# 4 - Two lines, a \ starting at half the left side
#                another starting at half the top isde
# 5 - One line, |
# 6 - Two lines, a | starting a quarter from the left
#                another starting a quarter from the right
# 7 - One line, -
# 8 - Two lines, a - starting a quarter from the top
#                another starting a quarter from the bottom
# 9 - An outline, can be described as
#     one | at the left, another at the right
#     one - at the top, another at the bottom
#     ~ This may cause the outlines to be twice as thick.
#     ~ Could be solved by only drawing one horiz and one vert line
#     ~ Then maybe only draw the missing if the pixel next to it doesn't do it
#     ~ Could also be split into 9 and 10 for horiz and vert.


def read_file(fn: str):
    img = Image.open(fn)

    # convert to black and white
    bw_img = img.convert('L')

    img.close()

    max_val_idx = (len(VALUES) - 1)
    width, height = bw_img.size
    matrix = list()
    for y in range(height):
        matrix.append(list())
        for x in range(width):
            # Clamp between values
            matrix[-1].append(
                round((255 - bw_img.getpixel((x, y))) / 255 * max_val_idx)
            )

    return matrix


def generate_test_matrix():
    """Generates a diagonal gradient"""
    num_values = len(VALUES)
    test = []
    for y in range(num_values + 1):
        test.append([])
        for x in range(num_values + 1):
            test[-1].append((y - x) % num_values)

    return test


def value1_lines(matrix):
    """Gets the single BL -> TR diagonal lines
    This function tries really hard to only traverse through the widest side"""
    val = 1
    lines = []

    # We'll go through x if it's the longest, or y if not
    # We need to do this because we want the diagonal lines to
    # go through every cell, we'd miss some if we didn't adapt

    # This variable decides if x(0) or y(1) should be traversed
    which_long_side = 'x' if len(matrix[0]) > len(matrix) else 'y'

    smallest_side, largest_side = sorted((len(matrix), len(matrix[0])))

    # TODO: Once it reaches the edge of the largest side, it just stops.
    #       I would want then to run from the bottom if y or right if x,
    #       starting at an idx of 1. This should cover it
    #
    #       Another way to do this would be to just swap to the opposite
    #       side of whichever I was just checking first. Picking up where
    #       it left off. This position/offset could be calculated as
    #       longest - smallest.
    idx = 0
    while idx < largest_side:
        # Set our starting point
        if which_long_side == 'x':
            x = idx
            y = 0
        else:
            x = 0
            y = idx

        line = []
        # Walk down the diagonal
        while 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
            if len(line) == 0 and matrix[y][x] >= val:
                if which_long_side == 'x':
                    # Start from top right
                    line.append((x + 1, y))

                else:
                    # Start from bottom left
                    line.append((x, y + 1))

            elif len(line) == 1 and not matrix[y][x] >= val:
                if which_long_side == 'x':
                    # End on bottom left of the last square
                    # I.e this one's top right
                    line.append((x + 1, y))

                else:
                    # End on top right of last square
                    # I.e. this one's bottom left
                    line.append((x, y + 1))

                # Then we update the lines and set up for the next loop
                lines.append((line[0], line[1]))
                line.clear()

            # We'll have the opposite heading depending
            # on which side we're walking from
            if which_long_side == 'x':
                x -= 1
                y += 1
            else:
                x += 1
                y -= 1

        # Add end point
        if len(line) == 1:
            if which_long_side == 'x':
                # This value was trial and error if I'm being honest
                # If I'm not being honest then this was product of my 503 IQ
                lines.append((line[0], (x + 1, y)))

            else:
                lines.append((line[0], (x, y + 1)))

        idx += 1

    return lines


def value5_lines(matrix):
    """Gets the single vertical lines"""
    val = 5
    lines = []

    # Travel along the x
    for x in range(len(matrix[0])):
        st_pt = []

        # The end of the line will be 1 coordinate down.
        # Otherwise a cell would become just a dot
        for y in range(len(matrix)):
            if len(st_pt) == 0 and matrix[y][x] >= val:
                st_pt.append((x + 0.5, y))

            elif len(st_pt) == 1 and not matrix[y][x] >= val:
                # We add the row above because this one doesn't have any
                st_pt.append((x + 0.5, y))

                # Then we update the lines and set up for the next loop
                lines.append((st_pt[0], st_pt[1]))
                st_pt = []

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if len(st_pt) == 1:
            lines.append((st_pt[0], (x + 0.5, len(matrix))))

    return lines


def value7_lines(matrix):
    """Gets the single horizontal lines"""
    val = 7
    lines = []

    # Travel along the y
    for y in range(len(matrix)):
        st_pt = []

        # The end of the line will be 1 coordinate down.
        # Otherwise a cell would become just a dot
        for x in range(len(matrix[0])):
            if len(st_pt) == 0 and matrix[y][x] >= val:
                st_pt.append((x, y + 0.5))

            elif len(st_pt) == 1 and not matrix[y][x] >= val:
                # We add the row above because this one doesn't have any
                st_pt.append((x, y + 0.5))

                # Then we update the lines and set up for the next loop
                lines.append((st_pt[0], st_pt[1]))
                st_pt = []

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if len(st_pt) == 1:
            lines.append((st_pt[0], (len(matrix[0]), y + 0.5)))

    return lines


def convert(pos, strt, unit):
    """Converts an xy to autogui pos"""
    return pos[0] * unit + strt[0], pos[1] * unit + strt[1]


def draw_lines(lines: list[tuple[int, int]],
               start: tuple[int, int], unit: int):
    for p1, p2 in lines:
        pyautogui.moveTo(convert(p1, start, unit))
        pyautogui.dragTo(convert(p2, start, unit))


def main():
    if len(argv) > 1:
        matrix = read_file(argv[1])
    else:
        matrix = generate_test_matrix()

    matrix = [[9, 9, 0, 9, 9,] for _ in range(5)]

    unit = 25

    # Program sleeps so that you can switch to the drawing program,
    # might want to wait for a click or hotkey instead.
    sleep(2)

    # Get start
    start = pyautogui.position()

    # Draw values
    draw_lines(value1_lines(matrix), start, unit)
    draw_lines(value5_lines(matrix), start, unit)
    draw_lines(value7_lines(matrix), start, unit)


if __name__ == "__main__":
    main()

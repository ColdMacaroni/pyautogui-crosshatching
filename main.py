import pyautogui
from time import sleep
from PIL import Image
from sys import argv
import numpy as np

pyautogui.PAUSE = 0.02

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


def get_diagonal_coords(matrix: list[list[int]], width: int, height: int, rtl: bool = False):
    if rtl:
        width_range = lambda: range(width - 1, -1 , -1)
    else:
        width_range = lambda: range(width)

    coord_matrix = [
        [
            (x, y)
            for x in width_range()
        ]
            for y in range(height)
    ]

    smallest_side, largest_side = sorted((height, width))

    for offset in range(-largest_side + 1, smallest_side):
        prev_x = prev_y = None

        # This will get me the diagonal i want
        diag_coords = np.diagonal(coord_matrix, offset, 1, 0)
        yield diag_coords

# -- BEGIN TERRIFYING CODE
def gen_double_diag_lines(matrix: list[list[int]], width: int, height: int, val: int, rtl: bool = False):
    ls = []

    diags = get_diagonal_coords(matrix, width, height, rtl)

    for diag in diags:
        prev_pt_top = None
        prev_pt_bot = None
        for (x, y) in zip(*diag):
            # -- Set starting point
            if prev_pt_top is None and matrix[y][x] >= val:
                prev_pt_top = (x + 0.5, y)

            # --
            # -- If the current block is not dark enough, we finish that line on the prev cell.
            elif prev_pt_top is not None and matrix[y][x] < val:
                ls.append((prev_pt_top, (x + rtl, y - 0.5)))
                prev_pt_top = None

            # --
            # -- If the line intersects a lighter cell, stop the line.
            if prev_pt_top is not None and (0 - (not rtl) < x < width - (not rtl)) and matrix[y][x + (-1 if rtl else 1)] < val:
                ls.append((prev_pt_top, (x + (not rtl), y + 0.5)))
                prev_pt_top = None


            # ---- Bottom line

            # -- Set starting point
            if prev_pt_bot is None and matrix[y][x] >= val:
                prev_pt_bot = (x + rtl, y + 0.5)

            # --
            # -- If the current block is not dark enough, we finish that line
            elif prev_pt_bot is not None and matrix[y][x] < val:
                ls.append((prev_pt_bot, (x + (1.5 if rtl else -0.5), y)))
                prev_pt_bot = None
            # --
            # -- If the line intersects a lighter cell, stop the line.
            if prev_pt_bot is not None and (y < height - 1) and matrix[y + 1][x] < val:
                ls.append((prev_pt_bot, (x + 0.5, y + 1)))
                prev_pt_bot = None

        # Check that there aren't any left over points
        if prev_pt_top is not None:
            ls.append((prev_pt_top, (x + (not rtl), y + 0.5)))
            prev_pt_top = None

        if prev_pt_bot is not None:
            ls.append((prev_pt_bot, (x + 0.5, y + 1)))
            prev_pt_bot = None

    return ls
# -- END TERRIFYING CODE



def value1_lines(matrix: list[list[int]], width: int, height: int):
    """Gets the single BL -> TR diagonal lines
    This function tries really hard to only traverse through the widest side"""
    val = 1
    lines = []

    # We're going top left to bottom right, so we need to flip the matrix
    coord_matrix = [
        [(x, y) for x in range(width - 1, -1, -1)]
        for y in range(height)]

    smallest_side, largest_side = sorted((height, width))

    for offset in range(-largest_side + 1, smallest_side):
        prev_x = prev_y = None

        # This will get me the diagonal i want
        diag_coords = np.diagonal(coord_matrix, offset, 1, 0)

        # First array contains x positions, the second: y.
        for x, y in zip(*diag_coords):
            # Line needs a start, top right
            if prev_x is None and matrix[y][x] >= val:
                prev_x = x
                prev_y = y

            # Line needs an end, bottom left
            elif prev_x is not None and not matrix[y][x] >= val:
                # Then we update the lines and set up for the next loop
                lines.append(((prev_x + 1, prev_y), (x + 1, y)))

                # Reset for next loop
                prev_x = prev_y = None

        # Add end point
        if prev_x is not None:
            lines.append(((prev_x + 1, prev_y), (x, y + 1)))

    return lines


def value2_lines(matrix: list[list[int]], width: int, height: int):
    """Gets the double BL -> TR diagonal lines"""
    val = 2

    lines = gen_double_diag_lines(matrix, width, height, val, rtl=True)

    return lines


def value3_lines(matrix: list[list[int]], width: int, height: int):
    """Gets the single TL -> BR diagonal lines"""
    val = 3
    lines = []

    # We're going top left to bottom right, so we need to flip the matrix
    coord_matrix = [
        [(x, y) for x in range(width)]
        for y in range(height)]

    smallest_side, largest_side = sorted((height, width))

    for offset in range(-largest_side + 1, smallest_side):
        prev_x = prev_y = None

        # This will get me the diagonal i want
        diag_coords = np.diagonal(coord_matrix, offset, 1, 0)

        # First array contains x positions, the second: y.
        for x, y in zip(*diag_coords):
            # Line needs a start, top right
            if prev_x is None and matrix[y][x] >= val:
                prev_x = x
                prev_y = y

            # Line needs an end, bottom left
            elif prev_x is not None and not matrix[y][x] >= val:
                # Then we update the lines and set up for the next loop
                lines.append(((prev_x, prev_y + 1), (x, y + 1)))

                # Reset for next loop
                prev_x = prev_y = None

        # Add end point
        if prev_x is not None:
            lines.append(((prev_x, prev_y), (x + 1, y + 1)))

    return lines


def value4_lines(matrix: list[list[int]], width: int, height: int):
    """Gets the double TL -> BR diagonal lines"""
    val = 4

    lines = gen_double_diag_lines(matrix, width, height, val, rtl=False)

    return lines


def value5_lines(matrix, width, height):
    """Gets the single vertical lines"""
    val = 5
    lines = []

    # Travel along the x
    for x in range(width):
        prev_x = prev_y = None

        # The end of the line will be 1 coordinate down.
        # Otherwise a cell would become just a dot
        for y in range(height):
            if prev_x is None and matrix[y][x] >= val:
                prev_x = x
                prev_y = y

            elif prev_x is not None and not matrix[y][x] >= val:
                # Add 0.5 to center
                lines.append(((prev_x + 0.5, prev_y), (x + 0.5, y)))

                # Reset
                prev_x = prev_y = None

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if prev_x is not None:
            lines.append(((prev_x + 0.5, prev_y), (x + 0.5, height)))

    return lines


def value6_lines(matrix, width, height):
    """Gets the double vertical lines"""
    val = 6
    lines = []

    off1 = 1/6
    off2 = 5/6

    # Travel along the x
    for x in range(width):
        prev_x = prev_y = None

        # The end of the line will be 1 coordinate down.
        # Otherwise a cell would become just a dot
        for y in range(height):
            if prev_x is None and matrix[y][x] >= val:
                prev_x = x
                prev_y = y

            elif prev_x is not None and not matrix[y][x] >= val:
                # Add 0.5 to center
                lines.append(((prev_x + off1, prev_y), (x + off1, y)))
                lines.append(((prev_x + off2, prev_y), (x + off2, y)))

                # Reset
                prev_x = prev_y = None

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if prev_x is not None:
            lines.append(((prev_x + off1, prev_y), (x + off1, height)))
            lines.append(((prev_x + off2, prev_y), (x + off2, height)))

    return lines


def value7_lines(matrix, width, height):
    """Gets the single horizontal lines"""
    val = 7
    lines = []

    # Travel along the y
    for y in range(height):
        prev_x = prev_y = None

        # The end of the line will be 1 coordinate down.
        # Otherwise a cell would become just a dot
        for x in range(width):
            if prev_x is None and matrix[y][x] >= val:
                prev_x = x
                prev_y = y

            elif prev_x is not None and not matrix[y][x] >= val:
                # Then we update the lines and set up for the next loop
                lines.append(((prev_x, prev_y + 0.5), (x, y + 0.5)))

                prev_x = prev_y = None

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if prev_x is not None:
            lines.append(((prev_x, prev_y + 0.5), (x + 1, y + 0.5)))

    return lines


def value8_lines(matrix, width, height):
    """Gets the single horizontal lines"""
    val = 8
    lines = []

    # We need to put them a sixth from the edge so that they're evenly spaced
    off1 = 1/6
    off2 = 5/6

    # Travel along the y
    for y in range(height):
        prev_x = prev_y = None

        # The end of the line will be 1 coordinate down.
        # Otherwise a cell would become just a dot
        for x in range(width):
            if prev_x is None and matrix[y][x] >= val:
                prev_x = x
                prev_y = y

            elif prev_x is not None and not matrix[y][x] >= val:
                # Then we update the lines and set up for the next loop
                # We add two lines, because yeah.
                # They're at 1/4 and 3/4
                # TODO! There has to be a better way of doing the second point
                lines.append(((prev_x, prev_y + off1), (x, y + off1)))
                lines.append(((prev_x, prev_y + off2), (x, y + off2)))

                prev_x = prev_y = None

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if prev_x is not None:
            lines.append(((prev_x, prev_y + off1), (width, y + off1)))
            lines.append(((prev_x, prev_y + off2), (width, y + off2)))

    return lines


def value9_lines(matrix, width, height):
    """Gets the outlines. This function is also horrible"""
    val = 9
    lines = []

    # Do horizontal lines
    for y in range(height):
        prev_ht_x = prev_ht_y = prev_hb_x = prev_hb_y = None

        # Check each horizontal line
        for x in range(width):
            # Top line, always drawn
            if prev_ht_x is None and matrix[y][x] >= val:
                prev_ht_x = x
                prev_ht_y = y

            elif prev_ht_x is not None and not matrix[y][x] >= val:
                # We only need to draw one because they'll overlap
                lines.append(((prev_ht_x, prev_ht_y), (x, y)))

                prev_ht_x = prev_ht_y = None

            # Bottom line, drawn when there isn't one below
            if prev_hb_x is None and matrix[y][x] >= val and (y == height - 1 or not matrix[y+1][x] >= val):
                prev_hb_x = x
                prev_hb_y = y

            elif prev_hb_x is not None and (not matrix[y][x] >= val or (y < height - 1 and not matrix[y+1][x] >= val)):
                # We only need to draw one because they'll overlap
                lines.append(((prev_hb_x, prev_hb_y + 1), (x, y + 1)))

                prev_hb_x = prev_hb_y = None


        # Add end point as end of image
        # This will happen if the line reaches to the end
        if prev_ht_x is not None:
            lines.append(((prev_ht_x, prev_ht_y), (x + 1, y)))

        if prev_hb_x is not None:
            lines.append(((prev_hb_x, prev_hb_y + 1), (x+1, y + 1)))

    # Do vertical lines
        # Travel along the x
    for x in range(width):
        prev_vl_x = prev_vl_y = prev_vr_x = prev_vr_y = None

        # Draw the left edge
        for y in range(height):
            if prev_vl_x is None and matrix[y][x] >= val:
                prev_vl_x = x
                prev_vl_y = y

            elif prev_vl_x is not None and not matrix[y][x] >= val:
                lines.append(((prev_vl_x, prev_vl_y), (x, y)))

                # Reset
                prev_vl_x = prev_vl_y = None

            # Draw line at the right
            if prev_vr_x is None and matrix[y][x] >= val and (x == width - 1 or not matrix[y][x + 1] >= val):
                prev_vr_x = x
                prev_vr_y = y

            elif prev_vr_x is not None and (not matrix[y][x] >= val or (x < width - 1 and not matrix[y][x + 1] >= val)):
                lines.append(((prev_vr_x+1, prev_vr_y), (x+1, y)))

                # Reset
                prev_vr_x = prev_vr_y = None

        # Add end point as end of image
        # This will happen if the line reaches to the end
        if prev_vl_x is not None:
            lines.append(((prev_vl_x, prev_vl_y), (x, height)))

        if prev_vr_x is not None:
            lines.append(((prev_vr_x + 1, prev_vr_y), (x + 1, y + 1)))



    return lines

def convert(pos, strt, unit):
    """Converts an xy to autogui pos"""
    return pos[0] * unit + strt[0], pos[1] * unit + strt[1]


def dist2(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    """Returns the distance squared of two points."""
    return pow(pos2[0] - pos1[0], 2) + pow(pos2[1] - pos1[1], 2)


def draw_lines(lines: list[tuple[int, int]],
               start: tuple[int, int], unit: int):
    # These are used later to calculate the most efficient next point.
    prev_p2 = (0, 0)
    for p1, p2 in lines:
        # Move the mouse to the closest end of the line and draw from there.
        if dist2(prev_p2, p1) <= dist2(prev_p2, p2):
            pyautogui.moveTo(convert(p1, start, unit))
            pyautogui.dragTo(convert(p2, start, unit))

        else:
            pyautogui.moveTo(convert(p2, start, unit))
            pyautogui.dragTo(convert(p1, start, unit))

        prev_p2 = p2


def main():
    if len(argv) > 1:
        matrix = read_file(argv[1])
    else:
        matrix = generate_test_matrix()

    # matrix = [[2, 0, 2, 2, 0, 2] for _ in range(5)]

    width = len(matrix[0])
    height = len(matrix)

    unit = 20

    # Program sleeps so that you can switch to the drawing program,
    # might want to wait for a click or hotkey instead.
    sleep(2)

    # Get start
    start = pyautogui.position()

    # Draw values
    draw_lines(value1_lines(matrix, width, height), start, unit)
    draw_lines(value2_lines(matrix, width, height), start, unit)
    draw_lines(value3_lines(matrix, width, height), start, unit)
    draw_lines(value4_lines(matrix, width, height), start, unit)
    draw_lines(value5_lines(matrix, width, height), start, unit)
    draw_lines(value6_lines(matrix, width, height), start, unit)
    draw_lines(value7_lines(matrix, width, height), start, unit)
    draw_lines(value8_lines(matrix, width, height), start, unit)
    draw_lines(value9_lines(matrix, width, height), start, unit)


if __name__ == "__main__":
    main()

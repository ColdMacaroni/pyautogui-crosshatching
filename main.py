import pyautogui
from time import sleep
from PIL import Image
from sys import argv

# How dark the image is
VALUES = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
ascii_vals = " .,-+;/=0#"
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


def main():
    if len(argv) > 1:
        matrix = read_file(argv[1])
    else:
        matrix = generate_test_matrix()

    # Program sleeps so that you can switch to the drawing program,
    # might want to wait for a click or hotkey instead.
    sleep(1)
    og_x, og_y = pyautogui.position()

    # draw em
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            print(ascii_vals[matrix[y][x]], end=" ")
        print()


if __name__ == "__main__":
    main()

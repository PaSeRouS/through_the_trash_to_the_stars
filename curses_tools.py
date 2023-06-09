import asyncio
from os import listdir
from os.path import isfile, join


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas. Erase text instead of drawing
    if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            # Check that current position it is not in a lower
            # right corner of the window.

            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/urses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment. Returns pair (rows number,
    colums number)"""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def sleep(tics=1):
    iteration_count = int(tics * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


def load_frame_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()


def load_multiple_frames(dirnames):
    return [
        load_frame_from_file(join(dirnames, file))
        for file in listdir(dirnames)
        if isfile(join(dirnames, file))
    ]

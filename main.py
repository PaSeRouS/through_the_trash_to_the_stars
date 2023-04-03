import asyncio
import curses
import random
import time

from animation import animate_frames
from space_trash import fly_garbage


TIC_TIMEOUT= 0.1


def load_frame_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()


async def blink(canvas, row, column, symbol='*', offset_tics=10):
    for _ in range(offset_tics):
        await asyncio.sleep(0)
  
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    canvas_rows, canvas_columns = canvas.getmaxyx()

    start_screen_row = 1
    start_screen_column = 1
    end_screen_row = canvas_rows - 2
    end_screen_column = canvas_columns - 2

    center_row = int(canvas_rows / 2)
    center_column = int(canvas_columns / 2)

    coroutines = []
    coroutines.append(fire(canvas, center_row, center_column))

    for _ in range(100):
        coroutines.append(
            blink(
                canvas,
                random.randint(start_screen_row, end_screen_row),
                random.randint(start_screen_column, end_screen_column),
                random.choice(['*', '+', '.', ':']),
                random.randint(1, 10)
            )
        )

    rocket_frame_1 = load_frame_from_file(
        'animations/rocket_frame_1.txt'
    )

    rocket_frame_2 = load_frame_from_file(
        'animations/rocket_frame_2.txt'
    )

    rocket_frames = (rocket_frame_1, rocket_frame_2)

    coro_rocket_anim = animate_frames(
        canvas,
        center_row,
        center_column,
        rocket_frames
    )
    coroutines.append(coro_rocket_anim)

    trash_frames = []

    trash_frames.append(load_frame_from_file(
            'animations/duck.txt'
        )
    )

    trash_frames.append(load_frame_from_file(
            'animations/hubble.txt'
        )
    )

    trash_frames.append(load_frame_from_file(
            'animations/lamp.txt'
        )
    )

    trash_frames.append(load_frame_from_file(
            'animations/trash_large.txt'
        )
    )

    trash_frames.append(load_frame_from_file(
            'animations/trash_small.txt'
        )
    )

    trash_frames.append(load_frame_from_file(
            'animations/trash_xl.txt'
        )
    )

    trash_coro = [
        fly_garbage(canvas, (column * 10) + 5, frame)
        for column, frame in enumerate(trash_frames)
    ]

    coroutines.extend(trash_coro)
    
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        
  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
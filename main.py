import asyncio
import curses
import random
import time

from animation import animate_spaceship, run_spaceship, fire
from curses_tools import get_frame_size, sleep, load_frame_from_file
from obstacles import show_obstacles
from space_trash import fly_garbage, obstacles


TIC_TIMEOUT= 0.1


async def blink(canvas, row, column, symbol='*', offset_tics=10):
    await sleep(offset_tics / 10)
  
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(2)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(0.5)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)


async def fill_orbit_with_garbage(canvas, coroutines, trash_frames):
    rows_number, columns_number = canvas.getmaxyx()
    border_size = 1
    while True:
        current_trash_frame = random.choice(trash_frames)
        rows_number, trash_column_size = get_frame_size(current_trash_frame)
        random_column = random.randint(
            border_size,
            columns_number - border_size
        )
        actual_column = min(
            columns_number - trash_column_size - border_size,
            random_column + trash_column_size - border_size,
        )

        trash_coroutines = fly_garbage(canvas, actual_column, current_trash_frame)
        coroutines.append(trash_coroutines)
        
        await sleep(2)


def draw(canvas):
    frame_container = []
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

    trash_coroutines = fill_orbit_with_garbage(canvas, coroutines, trash_frames)

    rocket_frame_1 = load_frame_from_file(
        'animations/rocket_frame_1.txt'
    )

    rocket_frame_2 = load_frame_from_file(
        'animations/rocket_frame_2.txt'
    )

    rocket_frames = (rocket_frame_1, rocket_frame_2)

    rocket_anim_coroutine = animate_spaceship(
        canvas,
        rocket_frames,
        frame_container
    )

    rocket_control_coroutine = run_spaceship(
        canvas,
        coroutines,
        center_row,
        center_column,
        frame_container
    )

    show_obstacles_coroutine = show_obstacles(canvas, obstacles)

    coroutines.append(rocket_anim_coroutine)
    coroutines.append(rocket_control_coroutine)
    coroutines.append(trash_coroutines)
    coroutines.append(show_obstacles_coroutine)
    
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

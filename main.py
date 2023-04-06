import asyncio
import curses
import random
import time

from animation import run_spaceship, fire
from curses_tools import get_frame_size, sleep, load_frame_from_file
from space_trash import fly_garbage, obstacles


TIC_TIMEOUT= 0.1


async def count_years(year_counter, level_duration_sec=3, increment=5):
    while True:
        await sleep(level_duration_sec)
        year_counter[0] += increment


async def show_year_counter(canvas, year_counter, start_year=1957):
    height, width = canvas.getmaxyx()

    counter_lenght = 9
    year_str_pos_y = 1
    year_str_pos_x = round(width / 2) - round(counter_lenght / 2)

    while True:
        current_year = start_year + year_counter[0]
        canvas.addstr(
            year_str_pos_y,
            year_str_pos_x,
            'Year {}'.format(current_year)
        )
        await asyncio.sleep(0)


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


async def fill_orbit_with_garbage(canvas, coroutines, trash_frames,  level,
        initial_timeout=5, complexity_factor=5, timeout_min=0.3):

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
        
        timeout_step = level[0] / complexity_factor
        garbage_respawn_timeout = initial_timeout - timeout_step

        if garbage_respawn_timeout <= timeout_min:
            garbage_respawn_timeout = timeout_min

        await sleep(garbage_respawn_timeout)


def draw(canvas):
    frame_container = []
    start_year = 1957
    level = [0]
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    canvas_rows, canvas_columns = canvas.getmaxyx()

    status_bar_height = 2
    sb_begin_y = sb_begin_x = 0
    status_bar = canvas.derwin(
        status_bar_height,
        canvas_columns,
        sb_begin_y,
        sb_begin_x
    )

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

    trash_coroutines = fill_orbit_with_garbage(
        canvas,
        coroutines,
        trash_frames,
        level
    )

    rocket_frame_1 = load_frame_from_file(
        'animations/rocket_frame_1.txt'
    )

    rocket_frame_2 = load_frame_from_file(
        'animations/rocket_frame_2.txt'
    )

    rocket_frames = (rocket_frame_1, rocket_frame_2)

    rocket_control_coroutine = run_spaceship(
        canvas,
        coroutines,
        center_row,
        center_column,
        rocket_frames,
        level,
        start_year
    )

    count_years_coroutine = count_years(level)
    show_year_counter_coroutine = show_year_counter(status_bar, level, start_year)

    coroutines.append(rocket_control_coroutine)
    coroutines.append(trash_coroutines)
    coroutines.append(count_years_coroutine)
    coroutines.append(show_year_counter_coroutine)
    
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

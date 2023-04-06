import asyncio
import curses
import itertools

from curses_tools import draw_frame, get_frame_size, sleep
from curses_tools import load_frame_from_file
from explosion import explode
from physics import update_speed
from space_trash import obstacles, obstacles_in_last_collisions


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


async def animate_spaceship(canvas, frames, frame_container):
    frames_cycle = itertools.cycle(frames)

    while True:
        frame_container.clear()
        spaceship_frame = next(frames_cycle)
        frame_container.append(spaceship_frame)
        await sleep(0.3)


async def run_spaceship(
    canvas,
    coroutines,
    start_row,
    start_column,
    frame_container
):

    height, width = canvas.getmaxyx()
    border_size = symbol_size = 1

    frame_size_y, frame_size_x = get_frame_size(frame_container[0])
    frame_pos_x = round(start_column) - round(frame_size_x / 2)
    frame_pos_y = round(start_row) - round(frame_size_y / 2)

    row_speed = column_speed = 0

    while True:
        for _ in range(2):
            direction_y, direction_x, spacebar = read_controls(canvas)

            if spacebar:
                shot_pos_x = frame_pos_x + round(frame_size_x / 2)
                shot_pos_y = frame_pos_y - symbol_size
                shot_coroutine = fire(canvas, shot_pos_y, shot_pos_x)
                coroutines.append(shot_coroutine)

            row_speed, column_speed = update_speed(
                row_speed,
                column_speed,
                direction_y,
                direction_x
            )

            frame_pos_x += column_speed
            frame_pos_y += row_speed

            frame_x_max = frame_pos_x + frame_size_x
            frame_y_max = frame_pos_y + frame_size_y

            field_x_max = width - border_size
            field_y_max = height - border_size

            frame_pos_x = min(frame_x_max, field_x_max) - frame_size_x
            frame_pos_y = min(frame_y_max, field_y_max) - frame_size_y

            frame_pos_x = max(frame_pos_x, border_size)
            frame_pos_y = max(frame_pos_y, border_size)

            draw_frame(canvas, frame_pos_y, frame_pos_x, frame_container[0])
            canvas.refresh()

            await sleep(0.1)

            draw_frame(
                canvas,
                frame_pos_y,
                frame_pos_x,
                frame_container[0],
                negative=True
            )

            for obstacle in obstacles:
                if obstacle.has_collision(frame_pos_y, frame_pos_x):
                    game_over_frame = load_frame_from_file(
                        'animations/gameover.txt'
                    )

                    game_over_coroutine = show_gameover(
                        canvas,
                        height,
                        width,
                        game_over_frame
                    )
                    coroutines.append(game_over_coroutine)
                    return


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed


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

    while 1 < row < max_row and 1 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(round(row), round(column)):
                obstacles_in_last_collisions.append(obstacle)
                await explode(canvas, obstacle.row, obstacle.column)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def show_gameover(canvas, window_height, window_width, frame):
    message_size_y, message_size_x = get_frame_size(frame)
    message_pos_y = round(window_height / 2) - round(message_size_y / 2)
    message_pos_x = round(window_width / 2) - round(message_size_x / 2)
    while True:
        draw_frame(canvas, message_pos_y, message_pos_x, frame)
        await asyncio.sleep(0)

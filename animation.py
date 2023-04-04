import asyncio
import itertools

from curses_tools import draw_frame, get_frame_size, sleep
from physics import update_speed


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
spaceship_frame = ''


async def animate_spaceship(canvas, frames):
    global spaceship_frame
    frames_cycle = itertools.cycle(frames)

    while True:
        spaceship_frame = next(frames_cycle)
        await sleep(0.3)


async def run_spaceship(canvas, start_row, start_column):
    height, width = canvas.getmaxyx()
    border_size = 1

    frame_size_y, frame_size_x = get_frame_size(spaceship_frame)
    frame_pos_x = round(start_column) - round(frame_size_x / 2)
    frame_pos_y = round(start_row) - round(frame_size_y / 2)

    row_speed = column_speed = 0

    while True:
        for _ in range(2):
            direction_y, direction_x, _ = read_controls(canvas)

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

            draw_frame(canvas, frame_pos_y, frame_pos_x, spaceship_frame)
            canvas.refresh()

            await sleep(0.3)
            
            draw_frame(
                canvas,
                frame_pos_y,
                frame_pos_x,
                spaceship_frame,
                negative=True
            )


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

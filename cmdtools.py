import time

from .fileutils import *


# ANSI escape codes: https://en.wikipedia.org/wiki/ANSI_escape_code
ANSI_ERASE_LINE = "\x1b[2K\r"
ANSI_CURSOR_UP = "\x1b[{n}A\r"
ANSI_CURSOR_DOWN = "\x1b[{n}C\r"


def progress_bar(progress, time_started):
    time_left = ((time.time() - time_started) / progress) - (time.time() - time_started)
    return "{:.2f}% [elapsed: {}, left: {}]".format(progress * 100,
                                                    format_seconds(time.time() - time_started),
                                                    format_seconds(time_left))


def format_speed(start_time, _bytes):
    diff = time.time() - start_time
    return "{size:>5}/s".format(size=(convert_file_size(_bytes / diff if diff > 0 else _bytes)))


def clear_line():
    print(ANSI_ERASE_LINE, end='\r', flush=True)
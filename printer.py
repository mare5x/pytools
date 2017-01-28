from threading import Lock

from .cmdtools import *
from . import pyutils

printer_lock = Lock()

reserved_line_buffers = [None]
line_count = 0


class printer:
    """ Multi-threaded multi-line stdout printer. 
    
    Usage:
        with pytools.printer() as p:
            for i in range(100):
                time.sleep(.1)
                p.print(i)
    """

    def __init__(self):
        self.line_number = get_new_line_number()
        global line_count
        with printer_lock:
            line_count += 1
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        global line_count
        with printer_lock:
            print(reserved_line_buffers[self.line_number])
            reserved_line_buffers[self.line_number] = None
            line_count -= 1

    def print(self, s):
        s = "{erase_line}{s}".format(erase_line=ANSI_ERASE_LINE, s=s)
        with printer_lock:
            reserved_line_buffers[self.line_number] = s
        
        print_lines()


def print_lines():
    with printer_lock:
        for line in reserved_line_buffers:
            if line is not None:
                print(line, flush=True)
        print(ANSI_CURSOR_UP.format(n=line_count), end='\r')


def get_new_line_number():
    free_index = pyutils.list_find(reserved_line_buffers, None)
    if free_index is not None:
        reserved_line_buffers[free_index] = ""
    else:
        reserved_line_buffers.append("")
        free_index = len(reserved_line_buffers) - 1

    return free_index

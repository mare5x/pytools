from threading import Lock

from . import cmdtools
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

    def __init__(self, number_of_lines=None):
        self.reserved_indices = reserve_lines(number_of_lines) if number_of_lines else []
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.exit()

    def get_input(self):
        """ Makes an input prompt at the end of this printer's lines and returns the input.

            WARNING: do NOT use this when multi-threading!
        """
        down_count = 0
        for index in range(self.reserved_indices[-1]):
            if reserved_line_buffers[index] is not None:
                down_count += 1

        print(cmdtools.ANSI_CURSOR_DOWN.format(n=down_count), end='\r')
        right_count = len(reserved_line_buffers[self.reserved_indices[-1]]) - len(cmdtools.ANSI_ERASE_LINE)
        print(cmdtools.ANSI_CURSOR_RIGHT.format(n=right_count), end='')

        ret = input()

        print(cmdtools.ANSI_CURSOR_UP.format(n=down_count + 2))  # return to top, +2 takes care of input() newline
        
        return ret

    def exit(self):
        global line_count
        with printer_lock:
            line_count -= len(self.reserved_indices)
            for index in self.reserved_indices:
                print(reserved_line_buffers[index])
                reserved_line_buffers[index] = None

    def clear_lines(self):
        global line_count
        with printer_lock:
            line_count -= len(self.reserved_indices)
            for index in self.reserved_indices:
                reserved_line_buffers[index] = None

    def print(self, s):
        lines = str(s).split('\n')
        lines = ["{erase_line}{s}".format(erase_line=cmdtools.ANSI_ERASE_LINE, s=s) for s in lines]

        if len(lines) != len(self.reserved_indices):
            self.clear_lines()
            self.reserved_indices = reserve_lines(len(lines))

        with printer_lock:
            for index in range(len(lines)):
                reserved_line_buffers[self.reserved_indices[index]] = lines[index]
        
        print_lines()


def print_lines():
    with printer_lock:
        for line in reserved_line_buffers:
            if line is not None:
                print(line, flush=True)
            else:
                print(cmdtools.ANSI_ERASE_LINE, end='\r')  # erase any left over artifacts
        print(cmdtools.ANSI_CURSOR_UP.format(n=line_count), end='\r')

def reserve_lines(n_lines):
    """ Reserves n_lines adjacent lines to be printed together.
    """

    # find if there is n_lines free spaces already
    base_index = -1
    n_free = 0
    for index, line in enumerate(reserved_line_buffers):
        if line == None:
            if n_free == 0:
                base_index = index
            n_free += 1
        else:
            n_free = 0
            base_index = -1

        if n_free >= n_lines:
            break

    indices = []
    if n_free >= n_lines and base_index != -1:
        for index in range(base_index, base_index + n_lines):
            reserved_line_buffers[index] = ""
            indices.append(index)
    else:
        base_index = len(reserved_line_buffers) if base_index == -1 else base_index

        for index in range(base_index, len(reserved_line_buffers)):
            reserved_line_buffers[index] = ""
            indices.append(index)

        base_index = len(reserved_line_buffers)
        for i in range(n_lines - len(indices)):
            reserved_line_buffers.append("")
            indices.append(base_index + i)

    global line_count
    line_count += n_lines

    return indices

def get_new_line_number():
    free_index = pyutils.list_find(reserved_line_buffers, None)
    if free_index is not None:
        reserved_line_buffers[free_index] = ""
    else:
        reserved_line_buffers.append("")
        free_index = len(reserved_line_buffers) - 1

    return free_index

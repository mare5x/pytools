""" Multi-threaded multi-line stdout printer. 
    NOTE: Terminal must support ANSI escape sequences.

    Blocks are printed in the order of their creation.

    Usage:
    with printer.block() as b:
        for i in range(10):
            b.print(i)
            time.sleep(.1)
"""

import threading

ANSI_ERASE_LINE = "\x1b[2K\r"
ANSI_CURSOR_UP = "\x1b[{n}A\r"

# TODO: a solution that doesn't abuse locks.
# Every operation that modifies the global state or 
# uses IO gets locked.
printer_lock = threading.RLock()

# Doubly linked list representation.
root_block = None
leaf_block = None
lines_used = 0
lines_total = 0

class block:
    """ Encapsulates a single multi-line string (=block). """

    def __init__(self, s=None, silent=False, split=True, max_line_width=120):
        """ silent: if True, exit silently when using a with statement (or .exit()). 
                Otherwise, the block is flushed. 

            split: if True, lines longer than max_line_width will get split up
                into shorter lines. Otherwise, they will get cut off.

            max_line_width: The character limit of each line. 
        """
        self.silent = silent
        self.split = split
        self.max_line_width = max_line_width

        self.prev = None
        self.next = None
        self.lines = []
        with printer_lock:
            if s is not None: 
                self.update(s)
            add_block(self)
    
    def __len__(self):
        """ NOTE: An object that doesn’t define a __bool__() method and 
            whose __len__() method returns zero is considered to be false in a Boolean context. """
        return len(self.lines)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.exit()

    def __iter__(self):
        for line in self.lines:
            yield line

    def exit(self):
        with printer_lock:
            if not self.silent:
                self.flush()
            self.discard()
            # If no more prints are issued, simply discarding would
            # leave behind old artifacts.
            if self.silent:
                print_lines()

    def split_string(self, s):
        long_lines = str(s).split('\n')
        lines = []
        for line in long_lines:
            if self.split:
                lines.extend(split_line(line, self.max_line_width))
            else:
                lines.append(cut_line(line, self.max_line_width))
        return lines

    def update(self, s):
        with printer_lock:
            lines = self.split_string(s)
            diff = len(lines) - len(self.lines)
            self.lines = lines
            update_line_count(diff)

    def discard(self):
        """ The block is removed, without printing anything. """
        with printer_lock:
            remove_block(self, self.silent)

    def flush(self):
        """ The block is outputted to the screen. """
        with printer_lock:
            for line in self.lines:
                print_line(line, flush=True)

    def print(self, s=None):
        """ Note: Calling print() changes the contents of the current block. All blocks are printed. """ 
        with printer_lock:
            if s is not None: 
                self.update(s)
            print_lines()

def cut_line(line, width):
    return line[:width]

def split_line(line, width):
    n = len(line)
    if n == 0: return [line]
    lines = []
    for i in range(0, n, width):
        left = i
        right = min(n, left + width)
        lines.append(line[left:right])
    return lines

def add_block(node):
    global root_block
    global leaf_block

    with printer_lock:
        if root_block is not None:
            leaf_block.next = node
        else:
            root_block = node

        node.prev = leaf_block
        leaf_block = node

def remove_block(node, silent):
    global lines_total, lines_used
    global root_block, leaf_block

    with printer_lock:
        lines_used -= len(node)
        if not silent:
            lines_total -= len(node)

        left = node.prev
        right = node.next
        if left is not None:  # See __len__ note as to why this is a None check.
            left.next = right
        else:
            root_block = right

        if right is not None:
            right.prev = left
        else:
            leaf_block = left

def update_line_count(diff):
    global lines_used, lines_total

    with printer_lock:
        lines_used += diff
        lines_total = max(lines_total, lines_used)

def print_line(s, **kwargs):
    with printer_lock:
        print(ANSI_ERASE_LINE, end='\r')
        print(s, **kwargs)

def print_blocks():
    with printer_lock:
        cur_block = root_block
        while cur_block is not None:
            for line in cur_block:
                print_line(line)
            cur_block = cur_block.next

def print_lines():
    with printer_lock:
        # It is assumed that the cursor position is correct when calling this function.
        print_blocks()

        # Print the remaining blank lines.
        # Without this, old lines might get printed (when a block shrinks).
        for i in range(lines_total - lines_used):
            print_line("")

        print(ANSI_CURSOR_UP.format(n=lines_total), end='\r', flush=True)
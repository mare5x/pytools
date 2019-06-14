""" File directory logging module. 
    
    Usage: tree() or as a standalone script (__name__ == '__main__').
"""

import os
import time
import sys

TAB_WIDTH = 4
MAX_LEVEL = 12  # Level 0 is just the current directory.

# Note: the default encoding for Python 3 source code is UTF-8.
CHAR_TABLE_UNICODE = {
    "EMPTY": ' ',
    "VERT_PIPE": '│',
    "VERT_MID_PIPE": '├',
    "HOR_PIPE": '─',
    "BOT_PIPE": '└'
}

CHAR_TABLE_ASCII = {
    "EMPTY": ' ',
    "VERT_PIPE": '|',
    "VERT_MID_PIPE": '+',
    "HOR_PIPE": '-',
    "BOT_PIPE": '\\'
}

def print_segment(head, tail, stream):
    # Example: |---
    stream.write("{}{}".format(head, tail * (TAB_WIDTH - 1)))

def tree(path, files=False, stream=sys.stdout, ascii_mode=False):
    """ Prints a tree-like view of the directory 'path'. 

        Emulates cmd: 'tree' command.

        IMPORTANT NOTE: Set the PYTHONIOENCODING environment 
        variable to utf-8 if you are getting encoding errors!
        On Windows check the chcp command.
        When redirecting to a file, console redirection might
        not work. In that case, pass in a utf-8 encoded file to stream.
    """

    char_table = CHAR_TABLE_ASCII if ascii_mode else CHAR_TABLE_UNICODE

    # Tree traversal is a recursive problem, however
    # os.walk is iterative, so we have to make do ...
    level_size = [0] * (MAX_LEVEL + 2)
    level_index = [0] * (MAX_LEVEL + 2)
    level_char = [''] * (MAX_LEVEL + 2)

    # Header information:
    # The path is also normalized because the level
    # is calculated using os.sep.
    path = os.path.abspath(path)
    stream.write("{}\n".format(time.strftime("%Y %b %d %H:%M:%S", time.gmtime())))
    stream.write(path)
    stream.write("\n\n")

    for dirpath, dirnames, filenames in os.walk(path):
        # + 1 to not have index out of bounds issues.
        level = dirpath.count(os.sep) - path.count(os.sep) + 1
        level_size[level] = len(dirnames)
        level_index[level] = 0
        level_index[level - 1] += 1

        if level_index[level - 1] == level_size[level - 1]:
            level_char[level - 1] = char_table["EMPTY"]
        else:
            level_char[level - 1] = char_table["VERT_PIPE"]

        # Necessary for correct output when printing files.
        if level_size[level] > 0:
            level_char[level] = char_table["VERT_PIPE"]
        else:
            level_char[level] = char_table["EMPTY"]

        for i in range(1, level - 1):
            print_segment(level_char[i], char_table["EMPTY"], stream)
        # The final part of a line looks different  |---DIR\n .
        # And also take aesthetic details into account (BOT_PIPE).
        if level > 1:
            c = char_table["VERT_MID_PIPE"]
            if level_index[level - 1] == level_size[level - 1]:
                c = char_table["BOT_PIPE"]
            print_segment(c, char_table["HOR_PIPE"], stream)

        stream.write(dirpath.split(os.sep)[-1] + '\n')

        if files:
            for filename in filenames:
                for i in range(1, level + 1):
                    print_segment(level_char[i], char_table["EMPTY"], stream)
                stream.write(filename + '\n')

            # An 'empty' line after listing files.
            if len(filenames) > 0:
                for i in range(1, level + 1):
                    print_segment(level_char[i], char_table["EMPTY"], stream)
                stream.write('\n')

        # Don't visit deeper levels, but print the MAX_LEVEL level.
        if level > MAX_LEVEL:
            dirnames[:] = []


# You can also run this module seperately.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    parser.add_argument("-f", action="store_true", help="Display file names in each directory.")
    args = parser.parse_args()

    tree(args.path, files=args.f)

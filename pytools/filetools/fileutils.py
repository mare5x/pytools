from datetime import datetime as dtime
from time import strftime, gmtime
import time
import os
from os.path import join, getsize, getmtime
from contextlib import contextmanager
import shutil
try:
    from os import walk
except ImportError:
    from scandir import walk
import sys
import logging
import hashlib
import glob


def get_date(for_file=False):
    if for_file:
        return "{}".format(strftime("%Y_%m_%d", gmtime()))
    else:
        return "{}".format(strftime("%Y %b %d %H:%M:%S", gmtime()))


def date_modified(path, pretty=False, traverse=False):
    if pretty:
        return time.ctime(getmtime(path))
    elif traverse:
        date = dtime.min
        for root, dirs, files in walk(path):
            if date_modified(root) > date:
                date = date_modified(root)
        return date
    else:
        return dtime.fromtimestamp(getmtime(path))


def name_from_path(path):
    path = os.path.realpath(path)
    return os.path.basename(path)
    

def create_dir(path):
    # dir_name = "{}".format(join(path, get_date(True)))
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


def remove_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def remove_file(path):
    if os.path.isfile(path):
        os.remove(path)


def zip_dir(path_to_zip, name=None, save_path=".\\"):
    if name:
        return shutil.make_archive(save_path + name, "zip", path_to_zip)
    return shutil.make_archive(save_path + get_date(for_file=True), "zip", path_to_zip)


def format_seconds(secs):
    """
    Calculate hours, minutes, seconds from seconds.

    Return tuple (h, min, s)
    """
    # divmod = divide and modulo -- divmod(1200 / 1000)  =  (1, 200)
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    if hours == 0:
        return "{mins:02.0f}:{secs:02.0f}".format(mins=mins, secs=secs)
    return "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(hours, mins, secs)


def normalize_path(path):
    return os.path.normcase(os.path.abspath(path))


def get_file_size(path):
    return convert_file_size(getsize(path))


def convert_file_size(_bytes):
    """ Return string of appropriate size for given bytes.

    Note:
        Units are in octets. E.g.: 1 MiB = 2**20 bytes (8 bits = 1 octet)
    """
    kb = _bytes / 1024

    if (kb / 1024**2) >= 1:
        return "{:.2f} GiB".format(kb / 1024**2)
    elif (kb / 1024) >= 1:
        return "{:.2f} MiB".format(kb / 1024)
    else:
        return "{:.2f} KiB".format(kb)


def parent_dir(path, rel=False):
    if rel:
        return os.path.relpath(os.path.join(path, os.pardir))
    return os.path.abspath(os.path.join(path, os.pardir))


def create_filename(full_path):
    """ c:/users/asdfasf/asdf.exe -> c:/users/asdfasf/asdf (1).exe
        asdf.exe -> asdf (1).exe
    """
    if not os.path.exists(full_path):
        return os.path.abspath(full_path)

    l_path, r_path = os.path.split(full_path)
    filename, extension = os.path.splitext(r_path)

    index = 1
    new_path = os.path.abspath(os.path.join(l_path, "{} ({}){}".format(filename, index, extension)))
    while os.path.exists(new_path):
        index += 1
        new_path = os.path.abspath(os.path.join(l_path, "{} ({}){}".format(filename, index, extension)))

    return new_path


def init_log_file(path="."):
    if path == ".":
        path = "{script}_Logs/".format(script=get_script_filename()[0])
        log_file = create_filename(
            "{path}/{script}_{date}.txt".format(path=path,
                                                script=get_script_filename()[0],
                                                date=get_date(True)))
    else:
        log_file = create_filename(path)
    os.makedirs(path, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(u"%(levelname)s:%(asctime)s:%(threadName)s: %(message)s")
    file_handler = logging.FileHandler(log_file, 'w', 'utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_script_filename():
    """ filename, extension
    """
    return os.path.splitext(os.path.basename(sys.argv[0]))


def create_empty_file(path, size):
    with open(path, 'wb') as f:
        f.truncate(size)
    return path


# @contextmanager
# def temp_file(name=None, mode='w+b', prefix='tmp', suffix='', dir=None, delete=True):
#     if name:
#         with tempfile.NamedTemporaryFile()


def join_files(out_path, in_path, *in_paths, out_mode='wb', in_mode='rb'):
    with open(out_path, mode=out_mode) as out_file:
        if type(in_path) == str:
            shutil.copyfileobj(open(in_path, mode=in_mode), out_file)
        else:
            for path in in_path:
                shutil.copyfileobj(open(path, mode=in_mode), out_file)
        for path in in_paths:
            shutil.copyfileobj(open(path, mode=in_mode), out_file)


def real_case_filename(path):
    """
    "c:/users/mare5/projects/backuper/logs/2016_apr_01.txt" -> 2016_Apr_01.txt
    "c:/users/mare5/projects/backuper/logs" -> Logs
    """
    path = glob.escape(os.path.abspath(path))  # if file name has a ?, * or [
    name = "{}[{}]".format(path[:-1], path[-1])
    found_path = glob.glob(name)
    if found_path:
        return found_path[0].rsplit('\\', 1)[-1]
    return path


def md5sum(path):
    """
    Generate a md5sum for the given path based on the file contents.
    Args:
        path: str, path to a file
    Returns:
        str, md5 checksum
        None -> cannot generate md5 checksum
    Note:
        md5 is exploitable!
    """
    if os.path.isfile(path):
        hash_md5 = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

from threading import Lock

lock = Lock()


def list_find(target_list, item):
    """ Find first occurrence of item in target_list and return its index or None if it wasn't found. """
    try:
        with lock:
            return target_list.index(item)
    except ValueError:
        return None
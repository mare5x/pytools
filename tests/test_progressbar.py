import time
import random
import concurrent.futures

from pytools import progressbar


def fuzz():
    time.sleep(random.random())

def test_iterator():
    iterable = [i for i in range(20)]
    for i in progressbar.progressbar(iterable, desc="Iterable test"):
        fuzz()

def test_dummy():
    with progressbar.progressbar(desc="Dummy test", show_time=False, bar_width=8) as p:
        for i in range(20):
            fuzz()
            p.update()

def test_manual():
    N = 20
    with progressbar.progressbar(total=N, desc="Manual test", show_time=False) as p:
        for i in range(N):
            fuzz()
            p.update()

def test_length():
    for i in progressbar.progressbar(range(10), desc="A" * 999, max_width=100):
        fuzz()

def test_block_iterator():
    iterable = [i for i in range(20)]
    for i in progressbar.blockbar(iterable, desc="Block iterable test"):
        fuzz()

def test_block_dummy():
    with progressbar.blockbar(desc="Block dummy test", show_time=False, bar_width=8) as p:
        for i in range(20):
            fuzz()
            p.update()

def test_block_manual():
    N = 20
    with progressbar.blockbar(total=N, desc="Block manual test") as p:
        for i in range(N):
            fuzz()
            p.update()

def test_block_length():
    for i in progressbar.blockbar(range(10), desc="A" * 999, max_width=100):
        fuzz()

def test_block_multiline():
    for i in progressbar.blockbar(range(20), desc="This blockbar spans multiple lines!\n\t"):
        fuzz()

def test_block_multi():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        ex.submit(test_block_iterator)
        ex.submit(test_block_dummy)
        ex.submit(test_block_manual)
        ex.submit(test_block_length)
        ex.submit(test_block_multiline)


if __name__ == "__main__":
    test_iterator()
    test_dummy()
    test_manual()
    test_length()
    test_block_iterator()
    test_block_dummy()
    test_block_manual()
    test_block_length()
    test_block_multiline()
    test_block_multi()
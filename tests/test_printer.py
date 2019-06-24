from pytools import printer
import concurrent.futures
import time
import random

def block_test0():
    with printer.block(silent=True) as b:
        for i in range(1, 11):
            b.print(i)
            if i % 2 == 0:
                b.flush()
            time.sleep(0.5)

def block_test1():
    with printer.block() as b:
        for i in range(10):
            b.print(i)
            time.sleep(.1)

        b.print("ASDF")
        b.flush()
        b.print("QWER\n\t{progress} ({downloaded} / {total}) [{speed}]")

def block_test2():
    block1 = printer.block("BLOCK1_0\n\tBLOCK1_1\n\t\tBLOCK1_2")
    block2 = printer.block()
    block3 = printer.block()
    for i in range(10):
        block2.print("BLOCK2_{}\n\tBLOCK2_{}".format(i, i))
        for j in range(1, 4):
            block3.print(('\n' * (j - 1)) + "BLOCK3_{}_{}".format(i, j))
            time.sleep(0.3)
        time.sleep(0.1)
    block1.exit()
    block2.exit()
    block3.exit()

def block_test3():
    content = [str(i) * i for i in range(9, -1, -1)]
    with printer.block(silent=True) as block:
        for line in content:
            block.print(line)
            time.sleep(0.33)

def block_test4(s):
    # Important test!
    with printer.block() as b:
        time.sleep(random.random())
        b.print(s)

def block_test5(s):
    with printer.block() as b:
        for i in range(len(s)):
            b.print(s[:i])
            time.sleep(0.05)
        for i in range(len(s)):
            b.print(s[:len(s) - i - 1])
            time.sleep(0.05)
        b.print(s)

def block_test_tall(silent, lines):
    blocks = [printer.block(silent=silent) for i in range(lines)]
    for i in range(lines):
        blocks[i].print(str(i) * i)
        time.sleep(0.05)
    for i in range(lines):
        blocks[lines - i - 1].exit()
        time.sleep(0.05)

def block_test_width(silent):
    n = 7
    blocks = [printer.block(silent=silent, max_line_width=2**i) for i in range(n)]
    for i in range(n):
        blocks[i].print(str(i) * blocks[i].max_line_width * 2)
        time.sleep(0.5)
    for block in blocks:
        block.exit()
        time.sleep(0.5)

def block_test_single(silent):
    with printer.block(silent=silent) as b:
        b.print("Single")

def thread_test1():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        ex.submit(block_test1)
        ex.submit(block_test3)

def thread_test2():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        ex.submit(block_test2)
        ex.submit(block_test1)

def thread_test3():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        ex.submit(block_test2)
        ex.submit(block_test3)

def thread_test4():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        ex.submit(block_test1)
        ex.submit(block_test2)
        ex.submit(block_test3)

def thread_test5():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        ex.submit(block_test0)
        ex.submit(block_test1)
        ex.submit(block_test2)
        ex.submit(block_test3)

def thread_test6():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        [ ex.submit(block_test4, str(i) * 5) for i in range(5) ]

def thread_test7():
    with concurrent.futures.ThreadPoolExecutor() as ex:
        [ ex.submit(block_test5, str(i) * 240) for i in range(5) ]

def split_tests():
    assert printer.split_line("", 8) == [""]
    assert printer.split_line("1234567", 8) == ["1234567"]
    assert printer.split_line("12345678", 8) == ["12345678"]
    assert printer.split_line("123456789", 8) == ["12345678", "9"]
    assert printer.split_line("12345678123456781", 8) == ["12345678", "12345678", "1"]

    assert printer.cut_line("", 8) == ""
    assert printer.cut_line("1", 8) == "1"
    assert printer.cut_line("1234567", 8) == "1234567"
    assert printer.cut_line("12345678", 8) == "12345678"
    assert printer.cut_line("123456789", 8) == "12345678"

def block_tests():
    block_test_single(False)
    block_test_single(True)
    block_test0()
    block_test1()
    block_test2()
    block_test3()
    block_test4("12345")
    block_test_tall(True, 10)
    block_test_tall(False, 10)
    block_test5("ASDF" * 40)
    block_test_width(True)
    block_test_width(False)

def block_thread_tests():
    thread_test1()
    thread_test2()
    thread_test3()
    thread_test4()
    thread_test5()
    thread_test6()
    thread_test7()

if __name__ == "__main__":
    split_tests()
    block_tests()
    block_thread_tests()

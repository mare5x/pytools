from pytools import cache


def test_lru():
    c = cache.LRUcache(maxsize=3)
    for i in range(1, 6): 
        c[i] = i
    print(c)  # 3, 4, 5
    
    c.get(3)  # 4, 5, 3
    c[6] = 6  # 5, 3, 6
    print(c)

    try:
        c[99]
    except KeyError as e:
        print("KeyError", e)
    
    del c[6]  # 5, 3
    print(c)

    c[7] = 7  # 5, 3, 7
    c[8] = 8  # 3, 7, 8
    c[3] = 9  # 7, 8, 9
    print(c)

    print(c.hits, c.misses)  # 2, 6

if __name__ == "__main__":
    test_lru()
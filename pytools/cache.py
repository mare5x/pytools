import collections.abc


class LRUcache(collections.abc.MutableMapping):
    
    class Entry:
        __slots__ = ["key", "val", "prev", "next"]
        def __init__(self, key, val, prev=None, next=None):
            self.key = key
            self.val = val
            self.prev = prev
            self.next = next

    def __init__(self, maxsize=8192):
        self.data = dict()
        self.maxsize = maxsize

        self.hits = 0
        self.misses = 0

        # The LRU mechanism is implemented using a linked list.
        # The least recently used item is always adjacent to the head.
        # That is because every access of an item moves that item next to the tail.
        self.head = self.Entry(None, None, prev=None, next=None)       # Oldest.
        self.tail = self.Entry(None, None, prev=self.head, next=None)  # Newest.
        self.head.next = self.tail
    
    def __getitem__(self, key):
        entry = self.data[key]
        self.hits += 1
        return self._get(entry).val

    def __setitem__(self, key, value):
        head, tail = self.head, self.tail
        entry = self.data.get(key, head)
        if entry is head:
            if len(self.data) >= self.maxsize:
                old = self._pop(head.next)
                del self.data[old.key]
            entry = self._push_back(key, value)
            self.data[key] = entry
            self.misses += 1
        else:
            self.hits += 1
            self._get(entry).val = value

    def __delitem__(self, key):
        self._pop(self.data[key])
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        s = "<{"
        s += ", ".join(("{}: {}".format(k, v.val) for k, v in self.data.items()))
        s += "}>"
        return s

    def _get(self, entry):
        self._pop(entry)
        return self._push_back(entry.key, entry.val, entry)

    def _push_back(self, key, value, entry=None):
        prev_tail, tail = self.tail.prev, self.tail
        if entry is None:
            entry = self.Entry(key, value, prev=prev_tail, next=tail)
        else:
            entry.val = value
            entry.prev = prev_tail
            entry.next = tail
        prev_tail.next = tail.prev = entry
        return entry

    def _pop(self, entry):
        left, right = entry.prev, entry.next
        left.next = right
        right.prev = left
        return entry
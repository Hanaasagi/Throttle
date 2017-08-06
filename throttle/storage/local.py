import time
from threading import RLock
from collections import OrderedDict


class LocalStorage:
    """
    >>> s = LocalStorage(2)
    >>> s.set('foo', 'bar', 5)
    >>> print(s['foo'])
    bar
    >>> import time
    >>> time.sleep(5)
    >>> s['foo']
    >>> s['hoge']
    >>> s.get('hoge')
    >>> s['hoge'] = 2
    >>> s['hoge']
    2
    >>> s.incr('hoge')
    >>> s['hoge']
    3
    >>> s['a'] = 1
    >>> s['b'] = 2
    >>> s['hoge']
    >>> s['a']
    1
    >>> s['c'] = 3
    >>> s['b']
    """

    def __init__(self, max_len=1000):
        super().__init__()
        self.max_len = max_len
        self.expired_map = {}
        self.data = OrderedDict()
        self.lock = RLock()


    def __getitem__(self, key):
        with self.lock:
            try:
                value = self.data[key]
            except KeyError:
                return None

            self.data.move_to_end(key)

            expired_time = self.expired_map.get(key, None)

            # key doesn't have expired_time
            if expired_time is None:
                return value

            if expired_time <= time.monotonic():
                del self.data[key]
                del self.expired_map[key]
                return None
            return value


    def get(self, key):
        return self[key]


    def __setitem__(self, key, value):
        with self.lock:
            if key in self.data:
                self.data.pop(key)
            elif len(self.data) == self.max_len:
                self.data.popitem(last=False)
            self.data[key] = value


    def set(self, key, value, seconds=None):
        self.data[key] = value
        if seconds is not None:
            self.expired_map[key] = time.monotonic() + seconds


    def incr(self, key):
        value = self.data[key] or 0
        if not isinstance(value, int):
            raise TypeError("only Integer can incr")
        self.data[key] = value + 1


    def expire(self, key, seconds):
        if key in self.data:
            expired_time = time.monotonic() + seconds
            self.expired_map[key] = expired_time
        else:
            raise KeyError("key doesn't exist")


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)

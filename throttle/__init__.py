import functools
from .storage import RedisStorage
from .storage import LocalStorage


class BaseThrottle:


    def __init__(self, rate):
        """
        :param rate: limit/duration etc. 1/s 2/m
        :return:     class instance
        """
        self.limit, self.duration = self.parse_rate(rate)
        # TODO


    def parse_rate(self, rate):
        """convert 'num/duration' string to a tuple (num, duration)
        :param rate: 'limit/duration' etc. '1/s' '2/m'
        :return:     a tuple (limit, duration)
        """
        num, period = rate.split('/')
        try:
            num = int(num)
            duration = {
                's': 1,
                'm': 60,
                'h': 3600,
                'd': 86400
            }[period[0]]
        except (ValueError, KeyError):
            raise ValueError('rate parse error')
        else:
            return num, duration



class Throttle(BaseThrottle):

    def __init__(self, rate):
        super().__Init__(rate)
        self.storage = LocalStorage()


    def enable_pass(self, key):
        result = storage.get(key)
        if result is None:
            storage(key, 1, expire=self.duration)
        else:
            count = int(result)
            if count < self.limit:
                storage.incr(key)
            else:
                storage.expire(key, self.duration)
                return False
        return True


    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.enable_pass('ababab')
                return func(*args, **kwargs)
            else:
                print('trigger the throttle')
        return wrapper


class RedisThrottle(BaseThrottle):


    def __init__(self, rate, host='localhost', port=6379, password=6379):
        super().__init__(rate)
        self.storage = RedisStorage(host, port, password)


    async def enable_pass(self, key):
        """whether pass the request
        :param key: a string ident eg. client IP
        :return:    boolean
        """
        storage = await self.storage.connect()
        result = await storage.get(key)  # str or None
        if result is None:
            storage.set(key, 1, expire=self.duration)
        else:
            count = int(result)
            if count < self.limit:
                storage.incr(key)
            else:
                storage.expire(key, self.duration)
                return False
        return True


    def __call__(self, func):
        """decorate a function which want to throttle
        :param func: the method or function you want to decorate
        :return: a wrapper
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if await self.enable_pass('ababab'):
                return await func(*args, **kwargs)
            else:
                # TODO
                from sanic.response import text
                return text('trigger the throttle', status=503)
        return wrapper


__all__ = ['Throttle', 'RedisThrottle']

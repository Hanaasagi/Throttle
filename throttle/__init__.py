import re
import functools
import inspect
from .storage import RedisStorage
from .storage import LocalStorage


class BaseThrottle:


    def __init__(self, rate, identify_name):
        """
        :param rate: limit/duration etc. 1/s 2/m
        :return:     class instance
        """
        self.limit, self.duration = self.parse_rate(rate)
        self.identify_name = identify_name


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


    def get_identify(self, func, *args, **kwargs):
        signature = inspect.signature(func)
        bind_arg = signature.bind(*args, **kwargs).arguments
        name_level_list = self.identify_name.split('.')
        identify = bind_arg.get(name_level_list[0])
        for name in name_level_list[1:]:
            if name.endswith(')'):
                # a function or method, call it
               capture = re.search(r'(.*)\((.*)\)', name)
               groups = capture.groups()
               identify = getattr(identify, groups[0])(groups[1].split(','))
            else:
                identify = getattr(identify, name)
        return identify



class Throttle(BaseThrottle):

    def __init__(self, rate, identify_name):
        super().__init__(rate, identify_name)
        self.storage = LocalStorage()


    def enable_pass(self, key):
        result = self.storage.get(key)
        if result is None:
            self.storage(key, 1, expire=self.duration)
        else:
            count = int(result)
            if count < self.limit:
                self.storage.incr(key)
            else:
                self.storage.expire(key, self.duration)
                return False
        return True


    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.enable_pass('ababab'):
                return func(*args, **kwargs)
            else:
                print('trigger the throttle')
        return wrapper


class RedisThrottle(BaseThrottle):


    def __init__(self, rate, identify_name, host='localhost', port=6379, password=''):
        super().__init__(rate, identify_name)
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
            identify = self.get_identify(func, *args, **kwargs)
            if await self.enable_pass(identify):
                return await func(*args, **kwargs)
            else:
                # TODO
                from sanic.response import text
                return text('trigger the throttle', status=503)
        return wrapper


__all__ = ['Throttle', 'RedisThrottle']

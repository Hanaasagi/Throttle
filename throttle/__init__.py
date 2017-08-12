import re
import functools
import inspect


class BaseThrottle:

    def __init__(self, rate, identify_getter, callback, storage):
        """
        :param rate:          limit/duration etc. 1/s 2/m
        :param identify_getter: a name or a callable use for geting identify
        :param callback:      how to do when exceed limit
        :return:              class instance
        """
        self.limit, self.duration = self.parse_rate(rate)
        self.identify_getter = identify_getter
        self.callback = callback
        self.storage = storage

    def parse_rate(self, rate):
        """convert 'limit/duration' string to a tuple (limit, duration)
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
        """get the identify"""
        # if it's a callable, just call and return
        if callable(self.identify_getter):
            return self.identify_getter()
        # if it's a string, like 'request.remote_addr' or 'self.get_remote_addr()'
        # so bind the signature and get 'request' from args or kwargs
        signature = inspect.signature(func)
        bind_arg = signature.bind(*args, **kwargs).arguments
        name_level_list = self.identify_getter.split('.')
        identify = bind_arg.get(name_level_list[0])
        for name in name_level_list[1:]:
            # solve nested name level
            if name.endswith(')'):
                # a function or method, pick up name and parameters, call it
                capture = re.search(r'(.*)\((.*)\)', name)
                groups = capture.groups()
                identify = getattr(identify, groups[0])(groups[1].split(','))
            else:
                identify = getattr(identify, name)
        return identify

    def enable_pass(self, key):
        """whether pass the request
        :param key: a string ident eg. client IP
        :return:    boolean
        """
        raise NotImplementedError

    def __call__(self, func):
        """decorate a function which want to throttle
        :param func: the method or function you want to decorate
        :return: a wrapper
        """
        raise NotImplementedError


class SyncThrottle(BaseThrottle):

    def enable_pass(self, key):
        result = self.storage.get(key)
        if result is None:
            self.storage.set(key, 1, seconds=self.duration)
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
        def wrapper(*args, **kwargs):
            identify = self.get_identify(func, *args, **kwargs)
            if self.enable_pass(identify):
                return func(*args, **kwargs)
            else:
                return self.callback(*args, **kwargs)
        return wrapper


class AsyncThrottle(BaseThrottle):

    async def enable_pass(self, key):
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
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            identify = self.get_identify(func, *args, **kwargs)
            if await self.enable_pass(identify):
                return await func(*args, **kwargs)
            else:
                return self.callback(*args, **kwargs)
        return wrapper


__all__ = ['SyncThrottle', 'AsyncThrottle']

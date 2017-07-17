import asyncio
import aioredis
import time
import functools


class RedisClient:
    """Redic Client Encapsulation"""


    def __init__(self, host='localhost', port=6379, password=''):
        """
        @param host:     redis server host name or address
        @param port:     redis server port
        @param password: redis server password
        @return:         class instance
        """
        self.host = host
        self.port = port
        self.password = password
        self.conn = None


    async def get_connection(self):
        """get redis connection"""
        if self.conn is not None:
            return self.conn
        self.conn = await aioredis.create_redis((self.host, self.port), encoding='utf-8')
        return self.conn


    async def get_atomic_connection(self):
        """get redis atomic connection"""
        # return self.get_connection().pipeline(True)
        conn = await self.get_connection()
        return conn.multi_exec()


class Throttle:


    def __init__(self, rate):
        """
        :param rate: limit/duration etc. 1/s 2/m
        :return:     class instance
        """
        self.limit, self.duration = self.parse_rate(rate)
        self.cli = RedisClient()


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


    async def enable_pass(self, key):
        """whether pass the request
        :param key: a string ident eg. client IP
        :return:    boolean
        """
        # TODO: cli need to place other place
        conn = await self.cli.get_connection()
        result = await conn.get(key)  # str or None
        if result is None:
            conn.set(key, 1, expire=self.duration)
        else:
            count = int(result)
            if count < self.limit:
                conn.incr(key)
            else:
                conn.expire(key, self.duration)
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

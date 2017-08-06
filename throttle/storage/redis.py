import aioredis


class RedisStorage:
    """Redis Stroage implementation"""


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


    async def connect(self):
        """get redis connection"""
        if self.conn is not None:
            return self.conn
        self.conn = await aioredis.create_redis((self.host, self.port), encoding='utf-8')
        return self.conn

    def __getarribute__(self, missing):
        return self.conn.missing

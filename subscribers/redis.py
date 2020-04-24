from .abstract import Subscribers


class RedisSubscribers(Subscribers):

    def __init__(self, pool):
        self.pool = pool

    async def list(self, user):
        return list(map(int, await self.pool.smembers(user)))

    async def push(self, subscriber, user):
        return bool(await self.pool.sadd(user, subscriber))

    async def remove(self, subscriber, user):
        return bool(await self.pool.srem(user, subscriber))

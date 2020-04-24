import asyncio

import aioredis

from config import BOT_TOKEN
from subscribers import RedisSubscribers
from bot import VasyukovObserver


async def main():
    redis_pool = await aioredis.create_redis_pool('redis://localhost')
    client = VasyukovObserver(RedisSubscribers(redis_pool))
    await client.start(BOT_TOKEN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

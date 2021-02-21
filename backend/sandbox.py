import asyncio

from scrapli_netconf.driver import AsyncNetconfScrape


MY_DEVICE = {
    "host": "192.168.152.102",
    "auth_username": "cisco",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "transport": "asyncssh",
}


async def main():
    async with AsyncNetconfScrape(**MY_DEVICE) as conn:
        # Platform drivers will auto-magically handle disabling paging for you
        result = await conn.get_config()
    breakpoint()


asyncio.run(main())

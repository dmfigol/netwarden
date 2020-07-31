import asyncio

from scrapli.driver.core import AsyncIOSXEDriver

MY_DEVICE = {
    "host": "192.168.153.105",
    "auth_username": "cisco",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "transport": "asyncssh",
}


async def main():
    async with AsyncIOSXEDriver(**MY_DEVICE) as conn:
        # Platform drivers will auto-magically handle disabling paging for you
        result = await conn.send_command("show version")
    breakpoint()


asyncio.run(main())

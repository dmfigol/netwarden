import logging
from typing import Callable, Any, Dict
from scrapli_netconf.driver import AsyncNetconfDriver

from netwarden.connections.base import Connection, ConnectionError

logger = logging.getLogger(__name__)

SSH_TRANSPORT = "asyncssh"
PRIORITY = 500


class NETCONFError(ConnectionError):
    pass


class NETCONF(Connection):
    NAME = "netconf"

    def __init__(
        self,
        name: str,
        host: str,
        username: str,
        password: str,
        platform: str,
        priority: int = PRIORITY,
    ) -> None:
        super().__init__(
            name=name,
            host=host,
            username=username,
            password=password,
            platform=platform,
            priority=priority,
        )
        self.connection = AsyncNetconfDriver(
            host=host,
            auth_username=username,
            auth_password=password,
            auth_strict_key=False,
            transport=SSH_TRANSPORT,
        )

    async def open(self) -> None:
        await self.connection.open()

    async def close(self) -> None:
        return await self.connection.close()

    async def handle(
        self,
        handler: Callable[..., Any],
        filter: str,
        **kwargs: Dict[str, Any],
    ):
        await self.raise_for_error()
        nc_response = await self.connection.get(filter_=filter)

        result = handler(nc_response.xml_result, **kwargs)
        return result

    async def update_availability(self) -> None:
        try:
            await self.open()
        except Exception:
            self.decrease_priority()
            logger.error(
                "%s connection to %s failed, new connection priority: %d",
                self.NAME.upper(),
                self.host,
                self.priority,
                exc_info=True,
            )
            self._enabled = False
        else:
            self._enabled = True

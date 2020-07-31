import logging
from typing import Callable, Any, Dict, TYPE_CHECKING
from scrapli.driver.core import AsyncIOSXEDriver

from netwarden.connections.base import Connection, ConnectionError

# from netwarden.connections import handlers
from netwarden.connections.ssh.constants import SSHParseMethod

if TYPE_CHECKING:
    from scrapli.driver import AsyncNetworkDriver

PLATFORM_TO_DRIVER = {"cisco_iosxe": AsyncIOSXEDriver}

logger = logging.getLogger(__name__)

SSH_TRANSPORT = "asyncssh"
PRIORITY = 500


class SSHError(ConnectionError):
    pass


class SSH(Connection):
    NAME = "ssh"

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
            priority=PRIORITY,
        )
        driver = PLATFORM_TO_DRIVER[platform]
        self.scrapli_conn: "AsyncNetworkDriver" = driver(
            host=host,
            auth_username=username,
            auth_password=password,
            auth_strict_key=False,
            transport=SSH_TRANSPORT,
        )

    async def open(self) -> None:
        await self.scrapli_conn.open()

    async def close(self) -> None:
        return await self.scrapli_conn.close()

    async def handle(
        self,
        handler: Callable[..., Any],
        command: str,
        parse_method: SSHParseMethod,
        **kwargs: Dict[str, Any],
    ):
        await self.raise_for_error()
        scrapli_result = await self.scrapli_conn.send_command(command)

        if parse_method is SSHParseMethod.TEXTFSM:
            data = scrapli_result.textfsm_parse_output()
        elif parse_method is SSHParseMethod.GENIE:
            data = scrapli_result.genie_parse_output()
        elif parse_method is SSHParseMethod.NULL:
            data = scrapli_result.result
        else:
            raise ValueError(f"Unknown parse method: {parse_method}")

        result = await handler(data, **kwargs)
        return result

    async def update_availability(self) -> None:
        try:
            await self.open()

        except Exception:
            self.decrease_priority()
            logger.error("SSH connection to %s failed, new connection priority: %d", self.host, self.priority, exc_info=True)
            self._enabled = False
        else:
            self._enabled = True

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Callable, Any, Dict, Optional

from netwarden.connections.handlers import HANDLERS

if TYPE_CHECKING:
    from fastapi import Request

DEFAULT_PRIORITY = 500
MIN_PRIORITY = 0
DEFAULT_PRIORITY_DECREMENT = 250


class ConnectionError(Exception):
    pass


T = TypeVar("T", bound="Connection")


class Connection(ABC):
    NAME = ""

    def __init__(
        self,
        name: str,
        host: str,
        username: str,
        password: str,
        platform: str,
        port: Optional[int] = None,
        priority: int = 100,
    ) -> None:
        self.name = name

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.platform = platform

        self.priority = priority

        self._enabled: Optional[bool] = None

    @abstractmethod
    async def open() -> None:
        pass

    @abstractmethod
    async def close() -> None:
        pass

    # @abstractmethod
    async def __aenter__(self) -> T:
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self.close()
        except Exception:
            pass

    async def is_enabled(self, force_check: bool = False) -> bool:
        if self._enabled is not None and not force_check:
            return self._enabled
        await self.update_availability()
        return self._enabled

    def get_handlers(self, key: str) -> Dict[str, Any]:
        result = HANDLERS[key][self.platform][self.NAME]
        return result

    @abstractmethod
    async def handle(self) -> Any:
        """Interface to handle data from the appropriate transport"""
        pass

    async def raise_for_error(self) -> None:
        """Raises ConnectionError if the connection can't be established"""
        is_enabled = await self.is_enabled()
        if not is_enabled:
            self.decrease_priority()
            raise ConnectionError(
                f"{self.NAME} connection to {self.host} couldn't be "
                f"Sestablished, new connection priority: {self.priority}"
            )

    @abstractmethod
    async def update_availability(self) -> None:
        pass

    async def parse(self, key: str, **kwargs: Dict[str, Any]) -> Any:
        handlers = self.get_handlers(key)
        results = [
            await self.handle(**handler_info, **kwargs)
            for handler_info in handlers["handlers"]
        ]
        result = handlers["collect_fn"](*results)
        return result

    # @abstractmethod
    # async def parse(self, key: str, **kwargs: Dict[str, Any]) -> Any:
    #     handler_info = HANDLERS[key][self.platform]
    #     endpoint = handler_info["endpoint"]
    #     handler = handler_info["handler"]

    #     is_enabled = await self.is_enabled()
    #     if not is_enabled:
    #         raise RESTCONFError("RESTCONF is not enabled")

    #     url = self.build_url(endpoint)
    #     response = await self.http_client.get(url, headers=RESTCONF.HEADERS)
    #     if response.is_error:
    #         raise RESTCONFError(f"Received error: {response.status_code}")

    #     data = response.json()
    #     result = handler(data, **kwargs)
    #     return result

    def decrease_priority(self, decrement: int = DEFAULT_PRIORITY_DECREMENT) -> None:
        self.priority -= decrement


def get_connection(request: "Request", device_name: str, connection_name: str) -> Any:
    connection = request.app.state.connections.get(device_name, {}).get(connection_name)
    return connection


def save_connection(
    request: "Request", device_name: str, connection: "Connection"
) -> None:
    device_connections = request.app.state.connections.get(device_name)
    if device_connections is None:
        device_connections = {}
        request.app.state.connections[device_name] = device_connections
    device_connections[connection.name] = connection


def get_or_create_connection(
    request: "Request",
    device_name: str,
    connection_name: str,
    factory: Callable[..., "Connection"],
    host: str,
    username: str,
    password: str,
    platform: str,
    **kwargs,
) -> "Connection":
    connection = get_connection(request, device_name, connection_name)
    if connection is None:
        connection = factory(
            name=connection_name,
            host=host,
            username=username,
            password=password,
            platform=platform,
            **kwargs,
        )
        save_connection(request, device_name, connection)
    return connection

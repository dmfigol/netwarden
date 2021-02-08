from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Callable, Any, Dict, Optional

from netwarden.connections.handlers import HANDLERS
from netwarden.utils import merge_dicts, no_op

if TYPE_CHECKING:
    from fastapi import Request

DEFAULT_PRIORITY = 500
MIN_PRIORITY = 0
DEFAULT_PRIORITY_DECREMENT = 250
DEFAULT_COLLECT_FUNC = merge_dicts


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
        priority: int = DEFAULT_PRIORITY,
    ) -> None:
        self.name = name
        self.priority = priority

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.platform = platform

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
        """Checks if the connection is established

        Args:
            force_check: if we need to force trying to establish connection
              before returning result. Default: False

        Returns:
            True if the connection is established, False - otherwise

        """
        # if connection was already tried to establish and we keep the result
        # and we don't need to force re-establishing connection
        if self._enabled is not None and not force_check:
            return self._enabled
        await self.update_availability()

        if self._enabled is None:
            raise ConnectionError(
                f"{self.NAME} connection to {self.host} was never established"
            )
        return self._enabled

    @abstractmethod
    async def update_availability(self) -> None:
        pass

    def get_handlers(self, key: str) -> Dict[str, Any]:
        """Retrieves handlers for specific request, platform and connection type.

        Args:
            key: type of requested information as described in handlers.py. For example,
              "version_sn"

        Returns:
            dictionary with the handlers for the request, platform and connection type
        """
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
                f"established, new connection priority: {self.priority}"
            )

    async def parse(self, key: str, **kwargs: Dict[str, Any]) -> Any:
        handlers = self.get_handlers(key)

        results = []
        for handler_info in handlers["handlers"]:
            if "handler" not in handler_info:
                # if handler function is not specified, use no_op function which
                # simply returns the input value
                handler_info["handler"] = no_op
            partial_result = await self.handle(**handler_info, **kwargs)
            results.append(partial_result)
        collect_func = handlers.get("collect_fn", DEFAULT_COLLECT_FUNC)
        result = collect_func(*results)
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

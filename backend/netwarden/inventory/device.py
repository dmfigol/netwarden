import logging
from operator import attrgetter
from typing import Iterable, Optional, Dict, Any, Type, TYPE_CHECKING

from dataclasses import dataclass, field

from netwarden.connections.base import ConnectionError

if TYPE_CHECKING:
    from netwarden.connections.base import Connection

logger = logging.getLogger(__name__)

@dataclass
class Device:
    name: str
    host: str
    username: str
    password: str
    platform: str
    connections: Dict[str, "Connection"] = field(default_factory=dict)

    def get_connection(self, conn_name: Optional[str] = None) -> "Connection":
        if conn_name is not None:
            return self.connections[conn_name]
        else:
            conn = max(self.connections.values(), key=attrgetter("priority"))
            logger.info("Device %r, selected connection: %r", self.name, conn.name)
            return conn

    def create_connection(
        self,
        conn_cls: Type["Connection"],
        conn_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Dict[str, Any]
    ) -> None:
        if conn_name is None:
            conn_name = conn_cls.NAME
        conn = conn_cls(
            name=conn_name,
            host=self.host,
            username=self.username,
            password=self.password,
            platform=self.platform,
        )
        self.connections[conn_name] = conn

    async def get_data(self, key: str, **kwargs: Dict[str, Any]) -> Any:
        """ TODO: implement proper retry mechanism with max number of attempts """
        conn = self.get_connection()
        try:
            result = await conn.parse(key, **kwargs)
            return result
        except ConnectionError:
            conn = self.get_connection()
            result = await conn.parse(key, **kwargs)
            return result

    @classmethod
    def from_netbox(
        cls, data: Dict[str, Any], connections: Iterable[Type["Connection"]]
    ) -> "Device":
        device = cls(
            name=data["name"],
            host=data["mgmt_ip"],
            username=data["username"],
            password=data["password"],
            platform=data["platform_slug"],
        )
        for conn_cls in connections:
            device.create_connection(conn_cls)
        return device


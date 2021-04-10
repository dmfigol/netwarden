import logging
from operator import attrgetter
from typing import Iterable, Optional, Dict, List, Any, Type, TYPE_CHECKING, cast

from pydantic import BaseModel, PrivateAttr

from netwarden.connections.base import ConnectionError
from netwarden.connections.handlers import HANDLERS


if TYPE_CHECKING:
    from netwarden.connections.base import Connection
    from netwarden.connections.netconf.connection import NETCONF

logger = logging.getLogger(__name__)


class Device(BaseModel):
    name: str
    host: str
    username: str
    password: str
    platform: str
    site: str = "N/A"
    vendor: str = "N/A"
    model: str = "N/A"
    _connections: Dict[str, "Connection"] = PrivateAttr(default_factory=dict)

    @property
    def connections(self) -> List["Connection"]:
        return sorted(
            self._connections.values(), key=attrgetter("priority"), reverse=True
        )

    def get_connection(
        self,
        conn_name: Optional[str] = None,
        allowed_connections=None,
        excluded_connections=None,
    ) -> "Connection":
        if conn_name is not None:
            # if specific connection type is required
            return self._connections[conn_name]
        else:
            #
            selected_conn = None
            for conn in self.connections:
                if excluded_connections:
                    if conn.name in excluded_connections:
                        continue
                if allowed_connections:
                    if conn.name in allowed_connections:
                        selected_conn = conn
            if selected_conn is None:
                raise ValueError(
                    f"Device {self.name!r}, a connection was not selected"
                )  # TODO: add custom error
            logger.info(
                "Device %r, selected connection: %r", self.name, selected_conn.name
            )
            return selected_conn

    def create_connection(
        self,
        conn_cls: Type["Connection"],
        conn_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Dict[str, Any],
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
        self._connections[conn_name] = conn

    async def get_data(self, key: str, **kwargs: Dict[str, Any]) -> Any:
        """ TODO: implement proper retry mechanism with max number of attempts """
        defined_connections = set(self.get_conn_and_handlers(key).keys())
        conn = self.get_connection(allowed_connections=defined_connections)
        try:
            result = await conn.parse(key, **kwargs)
            return result
        except ConnectionError:
            conn = self.get_connection(
                allowed_connections=defined_connections,
                excluded_connections={conn.name},
            )
            result = await conn.parse(key, **kwargs)
            return result

    def get_conn_and_handlers(self, key: str) -> Dict[str, Any]:
        return HANDLERS[key][self.platform]

    async def get_config(self, conn_name: str) -> Dict[str, str]:
        conn = self.get_connection(conn_name)
        if conn_name == "ssh":
            result = await conn.parse("cfg")
        elif conn_name == "restconf":
            restconf_cfg = await conn.parse("cfg")
            result = {"cfg": restconf_cfg}
        else:
            conn_ = cast("NETCONF", conn)
            await conn_.raise_for_error()
            nc_response = await conn_.connection.get_config()
            result = {"cfg": nc_response.result}
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
            vendor=data["vendor"],
            model=data["model"],
            site=data["site"],
        )
        # for conn_cls in connections:
        #     device.create_connection(conn_cls)
        return device

    def dump(self) -> Dict[str, Any]:
        return self.dict(exclude={"username", "password"})

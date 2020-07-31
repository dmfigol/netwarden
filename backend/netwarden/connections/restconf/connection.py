import logging
import re
from collections import ChainMap
from typing import Dict, Any, Optional, TYPE_CHECKING, Callable

from lxml import etree
from httpx import AsyncClient

from netwarden.connections.base import Connection, ConnectionError

# from netwarden.models.interface import Interface
from netwarden.models.node import Node

if TYPE_CHECKING:
    from netwarden.models.graph import Graph

IOS_XE_VERSION_RE = re.compile(r"\bVersion\s+(?P<sw_version>[\w.]+)\b")
PRIORITY = 700


logger = logging.getLogger(__name__)


class RESTCONFError(ConnectionError):
    pass


class RESTCONF(Connection):
    NAME = "restconf"
    HEADERS = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }
    AVAILABILITY_URL = "https://{host}/.well-known/host-meta"
    NAMESPACES = {"x": "http://docs.oasis-open.org/ns/xri/xrd-1.0"}

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
        # self.host = host
        # self.platform = platform
        self.http_client = AsyncClient(
            # headers=RESTCONF.HEADERS,
            auth=(self.username, self.password),
            # base_url=base_url,
            verify=False,
        )
        self._enabled: Optional[bool] = None
        self.root: Optional[bool] = None

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        return await self.http_client.aclose()

    async def update_availability(self) -> None:
        headers = {"Accept": "application/xrd+xml"}
        url = RESTCONF.AVAILABILITY_URL.format(host=self.host)
        try:
            response = await self.http_client.get(url, headers=headers)
            if response.is_error:
                self._enabled = False
                return
            xml_response = etree.fromstring(response.text)
            links = xml_response.xpath(
                "./x:Link[@rel='restconf']", namespaces=RESTCONF.NAMESPACES
            )
            first_link = links[0]
            restconf_root = first_link.get("href")
            self._enabled = True
            self.root = restconf_root
        except Exception:
            logger.error(
                "RESTCONF connection to %s failed, new connection priority: %d",
                self.host,
                self.priority,
                exc_info=True,
            )
            self._enabled = False

    # async def is_enabled(self, force_check: bool = False) -> bool:
    #     if self._enabled is not None and not force_check:
    #         return self._enabled
    #     await self.update_availability()
    #     return self._enabled

    def build_url(self, endpoint: str) -> str:
        if self.root is None:
            raise RESTCONFError(f"RESTCONF root is unknown")
        result = f"https://{self.host}{self.root}{endpoint}"
        return result

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

    async def handle(
        self, handler: Callable[[Any], Any], endpoint: str, **kwargs: Dict[str, Any]
    ) -> Any:
        await self.raise_for_error()
        url = self.build_url(endpoint)
        response = await self.http_client.get(url, headers=RESTCONF.HEADERS)
        if response.is_error:
            self.decrease_priority()
            raise RESTCONFError(f"Received error: {response.status_code}")

        data = response.json()
        result = handler(data, **kwargs)
        return result

    # async def get_vrf_list(self):
    #     response = await self.http_client.get("/restconf/data/native/vrf")
    #     response.raise_for_status()
    #     vrfs = []
    #     for vrf_data in response.json()["Cisco-IOS-XE-native:vrf"]["definition"]:
    #         vrf_name = vrf_data["name"]
    #         vrfs.append(vrf_name)
    #     return vrfs


def cisco_iosxe_parse_device_hw_data(data: Dict[str, Any]) -> Dict[str, Any]:
    tree_data = data["Cisco-IOS-XE-device-hardware-oper:device-hardware-data"]
    sw_version_raw = tree_data["device-hardware"]["device-system-data"][
        "software-version"
    ]
    sw_version = IOS_XE_VERSION_RE.search(sw_version_raw).group("sw_version")
    result = {
        "software_version": sw_version,
        "serial_number": tree_data["device-hardware"]["device-inventory"][0][
            "serial-number"
        ],
    }
    return result


## TODO: should this be reworked?
# def openconfig_lldp_parse(data: Dict[str, Any], graph: "Graph", node_name: str) -> None:
#     # node_interfaces = []
#     node = graph.get_or_create_node(node_name)
#     for interface_data in data["openconfig-lldp:interface"]:
#         interface_name = interface_data["name"]
#         interface = node.get_or_create_interface(interface_name)
#         # interface = Interface(name=interface_name, node=node)
#         # node_interface.append(interface)

#         neighbors = interface_data.get("neighbors")
#         if not neighbors:
#             continue

#         for neighbor_info in neighbors["neighbor"]:
#             neighbor_state = neighbor_info["state"]
#             remote_int_name = neighbor_state["port-description"]
#             remote_device_fqdn = neighbor_state["system-name"]
#             remote_node_name = Node.extract_hostname_from_fqdn(remote_device_fqdn)
#             remote_node = graph.get_or_create_node(remote_node_name)
#             remote_interface = remote_node.get_or_create_interface(remote_int_name)
#             interface.add_neighbor(remote_interface)


# HANDLERS = {
#     "version_sn": {
#         "cisco_iosxe": {
#             "endpoint": "/data/device-hardware-data",
#             "handler": cisco_iosxe_parse_device_hw_data,  # should return data in vendor-independent form
#         },
#         "cisco_iosxr": {"endpoint": "/", "handler": lambda x: None,},
#     },
#     "lldp": {
#         "cisco_iosxe": {
#             "endpoint": "/data/lldp/interfaces/interface",
#             "handler": openconfig_lldp_parse,
#         }
#     }
# }

# # dict[str, str]
# {
#     "version_sn": {
#         "cisco_iosxe": {
#             "restconf": {
#                 "collect_fn": ChainMap,
#                 "handlers": [{
#                     "endpoint": "/data/device-hardware-data",
#                     "handler": restconf.vendors.cisco_iosxe_parse_device_hw_data,
#                 }]
#             },
#             "scrapli_ssh": {
#                 "collect_fn": ChainMap,
#                 "handlers": [{
#                     "command": "show version",
#                     "handler": ssh.cisco_iosxe_parse_show_version
#                 }],
#             },
#         },
#     },
#     "lldp": {
#         "cisco_iosxe": {
#             "endpoint": "/data/lldp/interfaces/interface",
#             "handler": restconf.openconfig_lldp_parse,
#         }
#     }
# }

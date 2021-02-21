import re
from typing import Set, Tuple, TYPE_CHECKING

from netwarden.models.link import Link

if TYPE_CHECKING:
    from netwarden.models.node import Node


INTERFACE_NAME_RE = re.compile(
    r"(?P<interface_type>[a-zA-Z\-_ ]*)(?P<interface_num>[\d.\/]*)"
)

NORMALIZED_INTERFACES = (
    "FastEthernet",
    "GigabitEthernet",
    "TenGigabitEthernet",
    "FortyGigabitEthernet",
    "Ethernet",
    "Loopback",
    "Serial",
    "Vlan",
    "Tunnel",
    "Portchannel",
    "Management",
)


class Interface:
    def __init__(self, name: str, node: "Node") -> None:
        self.type, self.num = self.normalize_interface_name(name)
        self.node = node
        # self.device_name = device_name
        self.neighbors: Set["Interface"] = set()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}("
            f"name={self.name!r}, "
            f"node={self.node!r})"
        )

    def __str__(self) -> str:
        return f"{self.node}:{self.slug}"

    def __lt__(self, other) -> bool:
        return (self.node.name, self.name) < (other.node.name, other.name)

    def __eq__(self, other) -> bool:
        return (self.name, self.node) == (other.name, other.node)

    def __hash__(self) -> int:
        return hash((self.name, self.node.name))

    @property
    def name(self) -> str:
        return self.type + self.num

    @property
    def slug(self) -> str:
        return self.type[:2] + self.num

    def create_link_from_neighbors(self) -> Link:
        interfaces = [self, *self.neighbors]
        return Link(interfaces)

    @staticmethod
    def normalize_interface_name(interface_name: str) -> Tuple[str, str]:
        """Normalizes interface name
        For example:
            Gi0/1 is converted to GigabitEthernet1
            Te1/1 is converted to TenGigabitEthernet1/1
        """
        match = INTERFACE_NAME_RE.search(interface_name)
        if match:
            int_type = match.group("interface_type")
            normalized_int_type = Interface.normalize_interface_type(int_type)
            int_num = match.group("interface_num")
            return normalized_int_type, int_num
        raise ValueError(f"Does not recognize {interface_name} as an interface name")

    @staticmethod
    def normalize_interface_type(interface_type: str) -> str:
        """Normalizes interface type
        For example:
            G is converted to GigabitEthernet
            Te is converted to TenGigabitEthernet
        """
        int_type = interface_type.strip().lower()
        for norm_int_type in NORMALIZED_INTERFACES:
            if norm_int_type.lower().startswith(int_type):
                return norm_int_type

        return int_type

    def add_neighbor(self, interface: "Interface") -> None:
        self.neighbors.add(interface)

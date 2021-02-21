from typing import List, Dict

from netwarden.models.interface import Interface


class Node:
    cur_id = 1

    def __init__(self, name: str) -> None:
        self.name = name
        self.id = Node.cur_id
        Node.cur_id += 1

        self.name_to_interface: Dict[str, "Interface"] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}" f"(name={self.name!r})"

    def __str__(self) -> str:
        return self.name

    # @classmethod
    # def from_netbox_devices(cls, devices: List[Dict[str, Any]]) -> Dict[str, "Node"]:
    #     name_to_node: Dict[str, "Node"] = {}
    #     for device_data in devices:
    #         device_name = device_data["name"]
    #         node = Node(name=device_name)
    #         name_to_node[device_name] = node
    #     return name_to_node

    @property
    def interfaces(self) -> List["Interface"]:
        return list(self.name_to_interface.values())

    def get_or_create_interface(self, interface_name: str) -> "Interface":
        interface = self.name_to_interface.get(interface_name)
        if interface is None:
            interface = Interface(name=interface_name, node=self)
            self.add_interface(interface)
        return interface

    def add_interface(self, interface: "Interface") -> None:
        self.name_to_interface[interface.name] = interface

    @staticmethod
    def extract_hostname_from_fqdn(fqdn: str) -> str:
        """Extracts hostname from fqdn-like string
        For example, R1.cisco.com -> R1,  sw1 -> sw1"
        """
        return fqdn.split(".")[0]

    @staticmethod
    def normalize_name(node_name: str) -> str:
        if "." in node_name:
            result = Node.extract_hostname_from_fqdn(node_name)
        else:
            result = node_name
        return result

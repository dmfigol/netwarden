import logging
from typing import Dict, List, Any, TYPE_CHECKING, ValuesView

from netwarden.inventory.device import Device
from netwarden.connections.restconf.connection import RESTCONF
from netwarden.connections.ssh.connection import SSH
from netwarden.connections.netconf.connection import NETCONF

if TYPE_CHECKING:
    from netwarden.netbox import NetBox

logger = logging.getLogger(__name__)

CONNECTIONS = [RESTCONF, SSH, NETCONF]


class Inventory:
    def __init__(self, devices: Dict[str, Device] = None) -> None:
        if devices is None:
            devices = {}
        self.name_to_device = devices
        for device in self.devices:
            for conn_cls in CONNECTIONS:
                device.create_connection(conn_cls)

    def get_device(self, device_name: str) -> Device:
        return self.name_to_device[device_name]

    def add_device(self, device: Device, force: bool = False) -> None:
        if not force and device.name in self.name_to_device:
            raise ValueError(f"Device {device.name} already exists in the inventory")
        self.name_to_device[device.name] = device

    def __contains__(self, obj):
        if isinstance(obj, Device):
            return obj.name in self.name_to_device
        else:
            raise TypeError(f"Unknown operation for the object of type {type(obj)}")

    def __bool__(self) -> bool:
        return bool(self.name_to_device)

    def __len__(self) -> int:
        return len(self.name_to_device)

    @property
    def devices(self) -> ValuesView[Device]:
        return self.name_to_device.values()

    @classmethod
    def from_netbox_devices_list(cls, devices: List[Dict[str, Any]]) -> "Inventory":
        name_to_device: Dict[str, Device] = {}
        for device_data in devices:
            device = Device.from_netbox(device_data, connections=CONNECTIONS)
            name_to_device[device.name] = device
        inventory = cls(devices=name_to_device)
        return inventory

    @classmethod
    async def fetch_from_netbox(cls, netbox: "NetBox") -> "Inventory":
        # devices_coro = netbox.devices.list()
        # secrets_coro = netbox.secrets.list()
        # results = await asyncio.gather(devices_coro, secrets_coro)
        # devices_data, secrets_data = results
        devices_data = await netbox.devices.list()
        devices = netbox.parse_devices(devices=devices_data, secrets=[])
        inventory = cls.from_netbox_devices_list(devices)
        logger.info("%d devices imported from netbox", len(inventory))
        return inventory

    def dump(self):
        pass

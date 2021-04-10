import asyncio
import logging
from typing import cast

from fastapi import APIRouter, Request

from netwarden.inventory.inventory import Inventory
from netwarden.models.graph import Graph
from netwarden.netbox import NetBox


router = APIRouter()
logger = logging.getLogger(__name__)


async def _get_normalized_devices(request: Request):
    """ TODO: returns data and has a side effect """
    netbox = cast("NetBox", request.app.state.netbox)
    # devices_coro = netbox.devices.list()
    # secrets_coro = netbox.secrets.list()
    # results = await asyncio.gather(devices_coro, secrets_coro)
    # devices_data, secrets_data = results
    devices_data = await netbox.devices.list()
    devices = NetBox.parse_devices(devices=devices_data, secrets=None)
    inventory = cast(Inventory, request.app.state.inventory)
    if not inventory:
        request.app.state.inventory = Inventory.from_netbox_devices_list(devices)
    return devices


@router.get("/devices")
async def get_devices(request: Request):
    # devices = await _get_normalized_devices(request)
    inventory = cast(Inventory, request.app.state.inventory)
    fetch_data_tasks = []
    for device in inventory.devices:
        fetch_sw_sn_task = asyncio.create_task(device.get_data("version_sn"))
        fetch_data_tasks.append(fetch_sw_sn_task)

    await asyncio.gather(*fetch_data_tasks)
    devices = []
    for task, device in zip(fetch_data_tasks, inventory.devices):
        software_serial_data = task.result()
        device_dict = {
            **device.dump(),
            **software_serial_data,
        }
        devices.append(device_dict)

    return devices


@router.post("/devices/{device_name}/reboot")
async def reboot_device(device_name: str):
    await asyncio.sleep(10)
    logger.info("Device %r has been rebooted", device_name)
    return {
        "status": "success",
    }


@router.get("/devices/{device_name}/cfg")
async def get_config(request: Request, device_name: str, connection: str = "ssh"):
    inventory = cast(Inventory, request.app.state.inventory)
    device = inventory.get_device(device_name)
    # result = await device.get_data("cfg_plain")
    result = await device.get_config(connection)
    return result


@router.get("/network/lldp")
async def lldp_graph(request: Request):
    inventory = cast(Inventory, request.app.state.inventory)
    fetch_lldp_neighbors_tasks = [
        asyncio.create_task(device.get_data("lldp")) for device in inventory.devices
    ]

    await asyncio.gather(*fetch_lldp_neighbors_tasks)
    lldp_data = [
        (device.name, task.result())
        for task, device in zip(fetch_lldp_neighbors_tasks, inventory.devices)
    ]
    graph = Graph.from_lldp_data(lldp_data)
    return graph.dump()


@router.get("/ping")
async def ping(request: Request):
    # breakpoint()
    return {
        "status": "ok",
        "response": "pong",
    }

import asyncio
import logging
import logging.config
import os
import re
from typing import Optional, Dict, List, Any, cast, TYPE_CHECKING, Callable

from dynaconf import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from netwarden.constants import LOGGING_DICT
from netwarden.netbox import NetBox
from netwarden.inventory import Inventory
from netwarden.connections.restconf.connection import RESTCONF
from netwarden.connections.ssh.connection import SSH
from netwarden.models.node import Node
from netwarden.models.graph import Graph

if TYPE_CHECKING:
    from netwarden.connection import Connection

logging.config.dictConfig(LOGGING_DICT)
logger = logging.getLogger(__name__)

origins = ["http://localhost", "http://localhost:8081", "http://192.168.153.100:8081"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def make_netbox() -> NetBox:
    private_key_file = settings["netbox.private_key_file"]
    netbox_private_key = open(private_key_file, "r").read()
    netbox = NetBox(
        url=settings["netbox.host"],
        token=settings["netbox.token"],
        private_key=netbox_private_key,
    )
    return netbox


netbox = make_netbox()


@app.on_event("startup")
async def startup_event():
    # netbox = NetBox(url=settings["netbox.host"], token=settings["netbox.token"])
    app.state.netbox = netbox
    app.state.inventory = await Inventory.fetch_from_netbox(netbox)
    # app.state.connections = {}  # device_name -> {"restconf": <RESTCONF obj for device>}


@app.on_event("shutdown")
async def shutdown_event():
    tasks = []
    for device, connections in app.state.connections.items():
        for device_conn in connections.values():
            tasks.append(asyncio.create_task(device_conn.close()))
    await asyncio.gather(*tasks)


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# def create_fqdn(device_name: str, site_slug: str, domain: str) -> str:
#     result = f"{device_name.lower()}.{site_slug}.{domain}"
#     return result


# def build_device_id_to_login_creds(
#     secrets: List[Dict[str, Any]]
# ) -> Dict[str, Dict[str, str]]:
#     result = {}
#     for secret in secrets:
#         device_ref = secret.get("device")
#         secret_role = secret["role"]["slug"]
#         if device_ref is None or secret_role != "login-credentials":
#             continue
#         device_id = device_ref["id"]
#         login_creds = {"username": secret["name"], "password": secret["plaintext"]}
#         result[device_id] = login_creds
#     return result


# def normalize_devices(devices: List[Dict[str, Any]], secrets: List[Dict[str, Any]]):
#     device_id_to_login_creds = build_device_id_to_login_creds(secrets=secrets)

#     result = []
#     domain_name = settings["domain_name"]
#     for device in devices:
#         device_id = device["id"]
#         device_name = device["name"]
#         site = device["site"]["name"]
#         site_slug = device["site"]["slug"]
#         login_creds = device_id_to_login_creds.get(device_id, {})
#         primary_ip_data = device.get("primary_ip", {})
#         primary_ip = re.sub(r"/\d+", "", primary_ip_data.get("address", "N/A"))
#         vendor = device["device_type"]["manufacturer"]["name"]
#         model = device["device_type"]["model"]
#         platform_slug = device["platform"]["slug"]
#         platform = device["platform"]["name"]

#         normalized_device_dict = {
#             "name": device_name,
#             "fqdn": create_fqdn(
#                 device_name=device_name, site_slug=site_slug, domain=domain_name
#             ),
#             "vendor": vendor,
#             "model": model,
#             "platform_slug": platform_slug,
#             "platform": platform,
#             "sw_version": "N/A",
#             "mgmt_ip": primary_ip,
#             "site": site,
#             "console": {"server": "192.168.153.100", "port": 9000},
#             "username": login_creds.get("username", "N/A"),
#             "password": login_creds.get("password", "N/A"),
#         }
#         result.append(normalized_device_dict)
#     return result


async def _get_normalized_devices(request: Request):
    """ TODO: returns data and has a side effect """
    netbox = cast(NetBox, request.app.state.netbox)
    devices_coro = netbox.devices.list()
    secrets_coro = netbox.secrets.list()
    results = await asyncio.gather(devices_coro, secrets_coro)
    devices_data, secrets_data = results
    devices = netbox.parse_devices(devices=devices_data, secrets=secrets_data)
    inventory = cast(Inventory, request.app.state.inventory)
    if not inventory:
        request.app.state.inventory = Inventory.from_netbox_devices_list(devices)
    return devices


@app.get("/devices")
async def get_devices(request: Request):
    devices = await _get_normalized_devices(request)
    inventory = cast(Inventory, request.app.state.inventory)
    fetch_data_tasks = []
    # conn_cls = RESTCONF
    for device in inventory.devices:
        # device_name = device["name"]
        # restconf_conn = cast(
        #     conn_cls,
        #     get_or_create_connection(
        #         request=request,
        #         device_name=device_name,
        #         connection_name=conn_cls.NAME,
        #         factory=conn_cls,
        #         host=device.pop("mgmt_ip"),
        #         username=device["username"],
        #         password=device["password"],
        #         platform=device.pop("platform_slug"),
        #     ),
        # )
        fetch_sw_sn_task = asyncio.create_task(device.get_data("version_sn"))
        fetch_data_tasks.append(fetch_sw_sn_task)

    await asyncio.gather(*fetch_data_tasks)
    for task, device in zip(fetch_data_tasks, devices):
        software_serial_data = task.result()
        device.update(software_serial_data)

    # print(request.app.state.netbox)
    # netbox2 = cast(NetBox, request.app.state.netbox)
    return devices


def get_connection(request: Request, device_name: str, connection_name: str) -> Any:
    connection = request.app.state.connections.get(device_name, {}).get(connection_name)
    return connection


def save_connection(
    request: Request, device_name: str, connection: "Connection"
) -> None:
    device_connections = request.app.state.connections.get(device_name)
    if device_connections is None:
        device_connections = {}
        request.app.state.connections[device_name] = device_connections
    device_connections[connection.name] = connection


def get_or_create_connection(
    request: Request,
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


@app.post("/devices/{device_name}/reboot")
async def reboot_device(device_name: str):
    await asyncio.sleep(10)
    logger.info("Device %r has been rebooted", device_name)
    return {
        "status": "success",
    }


@app.get("/graph/lldp")
async def lldp_graph(request: Request):
    graph = Graph()
    devices = await _get_normalized_devices(request)
    parse_lldp_tasks = []
    for device in devices:
        device_name = device["name"]
        restconf_conn = cast(
            RESTCONF,
            get_or_create_connection(
                request=request,
                device_name=device_name,
                connection_name=RESTCONF.NAME,
                factory=RESTCONF,
                host=device.pop("mgmt_ip"),
                username=device["username"],
                password=device["password"],
                platform=device.pop("platform_slug"),
            ),
        )
        lldp_task = asyncio.create_task(
            restconf_conn.parse(
                "lldp",graph=graph, node_name=device_name
            )
        )
        parse_lldp_tasks.append(lldp_task)

    await asyncio.gather(*parse_lldp_tasks)
    graph.calculate_links()
    return graph.dump()

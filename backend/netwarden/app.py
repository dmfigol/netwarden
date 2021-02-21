import asyncio
import logging
import logging.config
from pathlib import Path
from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from netwarden.constants import LOGGING_DICT
from netwarden.inventory.inventory import Inventory
from netwarden.netbox import NetBox
from netwarden.routers.devices import router as devices_router
from netwarden.settings import settings

logging.config.dictConfig(LOGGING_DICT)
logger = logging.getLogger(__name__)

# origins = ["http://localhost", "http://localhost:8081", "http://192.168.152.100:8081"]
origins = ["*"]


app = FastAPI(
    openapi_url="/api/openapi.json", docs_url="/api/docs", redoc_url="/api/redoc"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices_router, prefix="/api")


def make_netbox() -> NetBox:
    private_key_filepath = settings.get("netbox.private_key_file")
    netbox_private_key = None
    if private_key_filepath:
        private_key_path = Path(private_key_filepath)
        if private_key_path.is_file():
            netbox_private_key = open(private_key_path, "r").read()
        else:
            logger.error("File %r was not found", private_key_filepath)
    netbox = NetBox(
        url=settings["netbox.host"],
        token=settings["netbox.token"],
        private_key=netbox_private_key,
    )
    return netbox


@app.on_event("startup")
async def startup_event():
    netbox = cast(NetBox, make_netbox())
    app.state.netbox = netbox
    app.state.inventory = await Inventory.fetch_from_netbox(netbox)
    # app.state.connections = {}  # device_name -> {"restconf": <RESTCONF obj for device>}  # noqa


@app.on_event("shutdown")
async def shutdown_event():
    tasks = []
    for device, connections in app.state.connections.items():
        for device_conn in connections.values():
            tasks.append(asyncio.create_task(device_conn.close()))
    await asyncio.gather(*tasks)

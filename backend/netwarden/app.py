import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://192.168.153.100:8080"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/devices")
async def get_devices():
    # replace with api calls to netbox and restconf to the devices
    return [
        {
            "name": "R1",
            "fqdn": "r1.krk.lab.dmfigol.me",
            "site": "Krakow",
            "mgmt_ip": "192.168.153.101",
            "sw_version": "N/A",
            "username": os.environ['DEVICE_USERNAME'],
            "password": os.environ['DEVICE_PASSWORD'],
            "console": {
                "server": "192.168.153.100",
                "port": 9000,
            }
        },
        {
            "name": "R2",
            "fqdn": "r2.krk.lab.dmfigol.me",
            "mgmt_ip": "192.168.153.102",
            "sw_version": "N/A",
            "username": os.environ['DEVICE_USERNAME'],
            "password": os.environ['DEVICE_PASSWORD'],
            "site": "Krakow",
            "console": {
                "server": "192.168.153.100",
                "port": 9001,
            }
        },
    ]


@app.post("/devices/{device_name}/reboot")
async def reboot_device(device_name: str):
    await asyncio.sleep(10)
    logger.info("Device %r has been rebooted", device_name)
    return {
        "status": "success",
    }

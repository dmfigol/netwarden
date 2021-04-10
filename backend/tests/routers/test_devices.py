from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest


from netwarden.app import app
from netwarden.inventory.inventory import Inventory
from netwarden.inventory.device import Device

INVENTORY = Inventory(
    {
        "R1": Device(
            name="R1",
            host="192.168.152.101",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R2": Device(
            name="R2",
            host="192.168.152.102",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R3": Device(
            name="R3",
            host="192.168.152.103",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R4": Device(
            name="R4",
            host="192.168.152.104",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R5": Device(
            name="R5",
            host="192.168.152.105",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R6": Device(
            name="R6",
            host="192.168.152.106",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R7": Device(
            name="R7",
            host="192.168.152.107",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R8": Device(
            name="R8",
            host="192.168.152.108",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R9": Device(
            name="R9",
            host="192.168.152.109",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
        "R10": Device(
            name="R10",
            host="192.168.152.110",
            username="cisco",
            password="cisco",
            platform="cisco_iosxe",
        ),
    },
)
app.state.inventory = INVENTORY
client = TestClient(app)


def test_ping():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json()["response"] == "pong"


@pytest.mark.asyncio
async def test_ping_async():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ping")
    assert response.status_code == 200
    assert response.json()["response"] == "pong"


@pytest.mark.asyncio
@pytest.mark.scrapli_replay
async def test_get_devices():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/devices")
    assert response.status_code == 200
    assert len(response.json()) == len(INVENTORY)

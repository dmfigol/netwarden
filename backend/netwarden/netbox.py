import logging
import re
import urllib.parse
from typing import Any, List, Dict, Union, Optional

import httpx
from dynaconf import settings

logger = logging.getLogger(__name__)


class NetBox:
    def __init__(self, url: str, token: str, private_key: Optional[str] = None) -> None:
        # self.token = token
        self.url = url
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {token}",
        }
        self.http_client = httpx.AsyncClient(headers=headers)
        self._session_key: Optional[str] = None
        self.private_key = private_key
        self.devices = DevicesCRUD(self)
        self.secrets = SecretsCRUD(self, private_key=private_key)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params=None,
        data=None,
        headers: Optional[Dict[str, str]] = None,
        is_json: bool = True,
        *args,
        **kwargs,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        url = self.build_url(endpoint)
        if is_json:
            json = data
            data = None
        else:
            data = data
            json = None
        response = await self.http_client.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json,
            data=data,
            *args,
            **kwargs,
        )
        response.raise_for_status()
        if response.content:
            return response.json()
        else:
            return None

    def build_url(self, endpoint: str) -> str:
        return f"{self.url}/api{endpoint}"

    async def _get(
        self, url, params=None, headers: Dict[str, str] = None, is_json: bool = True
    ) -> Any:
        return await self._request(
            "GET", url, params=params, headers=headers, is_json=is_json
        )

    async def _post(
        self,
        url,
        params=None,
        data=None,
        headers: Dict[str, str] = None,
        is_json: bool = True,
        # *args,
        # **kwargs
    ) -> Any:
        return await self._request(
            "POST", url, params=params, data=data, headers=headers, is_json=is_json
        )

    async def _put(
        self,
        url,
        params=None,
        data=None,
        headers: Dict[str, str] = None,
        is_json: bool = True,
    ) -> Any:
        return await self._request(
            "PUT", url, params=params, data=data, headers=headers, is_json=is_json
        )

    async def _delete(
        self, url, params=None, headers: Dict[str, str] = None, is_json: bool = True
    ) -> Any:
        return await self._request(
            "DELETE", url, params=params, headers=headers, is_json=is_json
        )

    @staticmethod
    def build_device_id_to_login_creds(
        secrets: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, str]]:
        result = {}
        for secret in secrets:
            device_ref = secret.get("device")
            secret_role = secret["role"]["slug"]
            if device_ref is None or secret_role != "login-credentials":
                continue
            device_id = device_ref["id"]
            login_creds = {"username": secret["name"], "password": secret["plaintext"]}
            result[device_id] = login_creds
        return result

    @staticmethod
    def create_fqdn(device_name: str, site_slug: str, domain: str) -> str:
        result = f"{device_name.lower()}.{site_slug}.{domain}"
        return result

    @staticmethod
    def parse_devices(devices: List[Dict[str, Any]], secrets: List[Dict[str, Any]]):
        device_id_to_login_creds = NetBox.build_device_id_to_login_creds(
            secrets=secrets
        )

        result = []
        domain_name = settings["domain_name"]
        for device in devices:
            device_id = device["id"]
            device_name = device["name"]
            site = device["site"]["name"]
            site_slug = device["site"]["slug"]
            login_creds = device_id_to_login_creds.get(device_id, {})
            primary_ip_data = device.get("primary_ip", {})
            primary_ip = re.sub(r"/\d+", "", primary_ip_data.get("address", "N/A"))
            vendor = device["device_type"]["manufacturer"]["name"]
            model = device["device_type"]["model"]
            platform_slug = device["platform"]["slug"]
            platform = device["platform"]["name"]

            normalized_device_dict = {
                "name": device_name,
                "fqdn": NetBox.create_fqdn(
                    device_name=device_name, site_slug=site_slug, domain=domain_name
                ),
                "vendor": vendor,
                "model": model,
                "platform_slug": platform_slug,
                "platform": platform,
                "sw_version": "N/A",
                "mgmt_ip": primary_ip,
                "site": site,
                "console": {"server": "192.168.153.100", "port": 9000},
                "username": login_creds.get("username", "N/A"),
                "password": login_creds.get("password", "N/A"),
            }
            result.append(normalized_device_dict)
        return result


class BaseCRUD:
    endpoint = ""

    def __init__(self, netbox: "NetBox"):
        self.netbox = netbox

    async def list(self) -> List[Dict[str, Any]]:
        response_data = await self.netbox._get(self.endpoint)
        return response_data["results"]

    async def get(self, id: str) -> Dict[str, Any]:
        response_data = await self.netbox._get(f"{self.endpoint}/{id}")
        return response_data

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response_data = await self.netbox._post(self.endpoint, data=data)
        return response_data

    async def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = "{endpoint}/{id}".format(endpoint=self.endpoint, id=data["id"])
        response_data = await self.netbox._put(url, data=data)
        return response_data

    async def delete(self, id: str) -> None:
        response_data = await self.netbox._delete(f"{self.endpoint}/{id}")
        return response_data


class DevicesCRUD(BaseCRUD):
    endpoint = "/dcim/devices"


class SecretsCRUD(BaseCRUD):
    endpoint = "/secrets/secrets"

    def __init__(self, netbox: "NetBox", private_key: Optional[str] = None):
        super().__init__(netbox=netbox)
        self._private_key = private_key
        self._session_key: Optional[str] = None

    async def list(self) -> List[Dict[str, Any]]:
        if self._session_key is None and self._private_key:
            self._session_key = await self.get_session_key(self._private_key)
        logger.debug("Session key was retrieved from NetBox")
        headers: Optional[Dict[str, str]] = None
        if self._session_key:
            headers = {
                "X-Session-Key": self._session_key,
            }
        response_data = await self.netbox._get(self.endpoint, headers=headers)
        return response_data["results"]

    async def get_session_key(self, private_key: Any) -> str:
        data = await self.netbox._post(
            "/secrets/get-session-key/?preserve-key=True",
            data=urllib.parse.urlencode({"private_key": private_key}),
            is_json=False,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return data["session_key"]

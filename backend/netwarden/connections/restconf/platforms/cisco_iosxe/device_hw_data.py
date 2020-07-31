import re
from typing import Dict, Any

IOS_XE_VERSION_RE = re.compile(r"\bVersion\s+(?P<sw_version>[\w.]+)\b")


def parse_device_hw_data(data: Dict[str, Any]) -> Dict[str, Any]:
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

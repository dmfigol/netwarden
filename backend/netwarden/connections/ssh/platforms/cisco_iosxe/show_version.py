from typing import Dict, Any


def parse_show_version_genie(data: Dict[str, Any]) -> Dict[str, Any]:
    version_data = data["version"]
    result = {
        "software_version": version_data["version"],
        "serial_number": version_data["chassis_sn"],
    }
    return result

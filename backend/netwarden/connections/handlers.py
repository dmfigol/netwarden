from collections import ChainMap

from netwarden.connections import restconf, ssh
from netwarden.connections.ssh.constants import SSHParseMethod
from netwarden.utils import merge_dicts

HANDLERS = {
    "version_sn": {
        "cisco_iosxe": {
            "restconf": {
                "collect_fn": ChainMap,
                "handlers": [{
                    "endpoint": "/data/device-hardware-data",
                    "handler": restconf.platforms.cisco_iosxe.parse_device_hw_data,
                }]
            },
            "ssh": {
                "collect_fn": ChainMap,
                "handlers": [{
                    "command": "show version",
                    "handler": ssh.platforms.cisco_iosxe.parse_show_version_genie,
                    "parse_method": SSHParseMethod.GENIE
                }],
            },
        },
    },
    # "lldp": {
    #     "cisco_iosxe": {
    #         "restconf": {
    #             "collect_fn": ChainMap,
    #             "handlers": [{
    #                 "endpoint": "/data/lldp/interfaces/interface",
    #                 "handler": restconf.openconfig_lldp_parse,
    #             }]
    #         }

    #     }
    # }
}

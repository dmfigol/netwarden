from netwarden.connections.restconf.openconfig import (
    parse_openconfig_lldp as restconf_parse_oc_lldp,
)

from netwarden.connections.restconf.platforms.cisco_iosxe import (
    parse_device_hw_data as restconf_iosxe_parse_device_hw_data,
)
from netwarden.connections.ssh.constants import SSHParseMethod
from netwarden.connections.ssh.platforms.cisco_iosxe import (
    parse_show_version_genie as ssh_iosxe_parse_show_version_genie,
    parse_show_run as ssh_iosxe_parse_show_run,
    parse_show_lldp_neighbors_detail_textfsm as ssh_iosxe_parse_show_lldp_neighbors,
)


# from netwarden import utils


HANDLERS = {
    "version_sn": {
        "cisco_iosxe": {
            "restconf": {
                # "collect_fn": merge_dicts,  # default
                "handlers": [
                    {
                        "endpoint": "/data/device-hardware-data",
                        "handler": restconf_iosxe_parse_device_hw_data,
                    }
                ]
            },
            "ssh": {
                "handlers": [
                    {
                        "command": "show version",
                        "handler": ssh_iosxe_parse_show_version_genie,
                        "parse_method": SSHParseMethod.GENIE,
                    }
                ],
            },
        },
    },
    "cfg": {
        "cisco_iosxe": {
            "ssh": {
                "handlers": [
                    {
                        "command": "show run",
                        "handler": ssh_iosxe_parse_show_run,
                        "parse_method": SSHParseMethod.NULL,
                    }
                ],
            },
            "restconf": {
                "handlers": [
                    {
                        "endpoint": "/data/native",
                        # "handler": utils.no_op,
                    },
                    {
                        "endpoint": "/data/openconfig-interfaces:interfaces",
                        # "handler": utils.no_op,
                    },
                    {
                        "endpoint": "/data/openconfig-bgp:bgp",
                        # "handler": utils.no_op,
                    },
                    {
                        "endpoint": "/data/openconfig-acl:acl",
                        # "handler": utils.no_op,
                    },
                ]
            },
        },
    },
    "lldp": {
        "cisco_iosxe": {
            "restconf": {
                "handlers": [
                    {
                        "endpoint": "/data/lldp/interfaces/interface",
                        "handler": restconf_parse_oc_lldp,
                    }
                ]
            },
            "ssh": {
                "handlers": [
                    {
                        "command": "show lldp neighbors detail",
                        "handler": ssh_iosxe_parse_show_lldp_neighbors,
                        "parse_method": SSHParseMethod.TEXTFSM,
                    }
                ],
            },
        }
    },
}

from netwarden.connections import restconf, ssh
from netwarden.connections.ssh.constants import SSHParseMethod
# from netwarden import utils


HANDLERS = {
    "version_sn": {
        "cisco_iosxe": {
            "restconf": {
                # "collect_fn": merge_dicts,  # default
                "handlers": [{
                    "endpoint": "/data/device-hardware-data",
                    "handler": restconf.platforms.cisco_iosxe.parse_device_hw_data,
                }]
            },
            "ssh": {
                "handlers": [{
                    "command": "show version",
                    "handler": ssh.platforms.cisco_iosxe.parse_show_version_genie,
                    "parse_method": SSHParseMethod.GENIE
                }],
            },
        },
    },
    "cfg": {
        "cisco_iosxe": {
            "ssh": {
                "handlers": [{
                    "command": "show run",
                    "handler": ssh.platforms.cisco_iosxe.parse_show_run,
                    "parse_method": SSHParseMethod.NULL
                }],
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
                    }
                ]
            },
        },
    },
    "lldp": {
        "cisco_iosxe": {
            "restconf": {
                "handlers": [{
                    "endpoint": "/data/lldp/interfaces/interface",
                    "handler": restconf.openconfig.parse_openconfig_lldp,
                }]
            },
            "ssh": {
                "handlers": [{
                    "command": "show lldp neighbors detail",
                    "handler": ssh.platforms.cisco_iosxe.parse_show_lldp_neighbors_detail_textfsm,  # noqa: E501
                    "parse_method": SSHParseMethod.TEXTFSM
                }],
            },
        }
    }
}

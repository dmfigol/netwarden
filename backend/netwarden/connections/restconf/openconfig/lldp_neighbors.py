
# currently:
# fetch lldp data using restconf, as we parse it, create interface and node objects
# what we want: similar parsing for restconf and SSH data
# solutions
# 1. convert ssh result to openconfig
# 2. convert both ssh result and openconfig to something we come up with

# TODO: should this be reworked?

from typing import Dict, List, Any

from netwarden.models.graph import LLDPNeighborInterface



# def openconfig_lldp_parse(data: Dict[str, Any], graph: "Graph", node_name: str) -> None:
#     # node_interfaces = []
#     node = graph.get_or_create_node(node_name)
#     for interface_data in data["openconfig-lldp:interface"]:
#         interface_name = interface_data["name"]
#         interface = node.get_or_create_interface(interface_name)
#         # interface = Interface(name=interface_name, node=node)
#         # node_interface.append(interface)

#         neighbors = interface_data.get("neighbors")
#         if not neighbors:
#             continue

#         for neighbor_info in neighbors["neighbor"]:
#             neighbor_state = neighbor_info["state"]
#             remote_int_name = neighbor_state["port-description"]
#             remote_device_fqdn = neighbor_state["system-name"]
#             remote_node_name = Node.extract_hostname_from_fqdn(remote_device_fqdn)
#             remote_node = graph.get_or_create_node(remote_node_name)
#             remote_interface = remote_node.get_or_create_interface(remote_int_name)
#             interface.add_neighbor(remote_interface)

def parse_openconfig_lldp(data: Dict[str, Any]) -> Dict[str, List[LLDPNeighborInterface]]:
    result: Dict[str, List[LLDPNeighborInterface]] = {}  # GigabitEthernet2 -> [(GigabitEthernet1, R1)]
    for interface_data in data["openconfig-lldp:interface"]:
        interface_name = interface_data["name"]  # full interface name form, e.g. GigabitEthernet2

        neighbors = interface_data.get("neighbors")
        if not neighbors:
            continue

        lldp_neighbors: List[LLDPNeighborInterface] = []
        for neighbor_info in neighbors["neighbor"]:
            neighbor_state = neighbor_info["state"]
            remote_int_name = neighbor_state["port-description"]
            remote_device_fqdn = neighbor_state["system-name"]
            lldp_neighbor = LLDPNeighborInterface(remote_int_name, remote_device_fqdn)
            lldp_neighbors.append(lldp_neighbor)
        result[interface_name] = lldp_neighbors
    return result
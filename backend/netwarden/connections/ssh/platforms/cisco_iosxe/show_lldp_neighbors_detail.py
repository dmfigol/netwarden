from collections import defaultdict
from typing import Dict, Any, List

from netwarden.models.graph import LLDPNeighborInterface


def parse_show_lldp_neighbors_detail_textfsm(
    data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    result: Dict[str, List[LLDPNeighborInterface]] = defaultdict(list)
    for lldp_neighbor_data in data:
        interface = lldp_neighbor_data["local_interface"]
        neighbor_interface = lldp_neighbor_data["neighbor_interface"]
        neighbor_node = lldp_neighbor_data["neighbor"]
        lldp_neighbor = LLDPNeighborInterface(neighbor_interface, neighbor_node)
        result[interface].append(lldp_neighbor)
    return result

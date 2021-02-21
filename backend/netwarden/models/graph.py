import logging
from typing import (
    Dict,
    List,
    ValuesView,
    Any,
    Set,
    Iterable,
    NamedTuple,
    Tuple,
)
from netwarden.models.node import Node
from netwarden.models.link import Link

logger = logging.getLogger(__name__)


class LLDPNeighborInterface(NamedTuple):
    interface: str
    node: str  # could be FQDN


class Graph:
    def __init__(self):
        self.name_to_node: Dict[str, Node] = {}
        self.links: Set["Link"] = set()

    @classmethod
    def from_lldp_data(
        cls, lldp_data: Iterable[Tuple[str, Dict[str, List[LLDPNeighborInterface]]]]
    ):
        graph = cls()
        for node_name, lldp_neighbors in lldp_data:
            # logger.info(graph.name_to_node)
            node = graph.get_or_create_node(node_name)
            # logger.info("Node %s.%d has been created", node.name, node.id)
            # logger.info(graph.name_to_node)
            for interface, lldp_neighbors in lldp_neighbors.items():
                interface = node.get_or_create_interface(interface)
                if len(lldp_neighbors) > 1:  # more than 2 devices on the link, skipping
                    logger.warning(
                        "%s.%s: more than 2 lldp neighbors found",
                        node_name,
                        interface.slug,
                    )
                    continue
                lldp_neighbor = lldp_neighbors[0]
                remote_node = graph.get_or_create_node(lldp_neighbor.node)

                # logger.info("Node %s.%d has been created", remote_node.name, remote_node.id)
                # logger.info(graph.name_to_node)
                remote_interface = remote_node.get_or_create_interface(
                    lldp_neighbor.interface
                )
                link = Link([interface, remote_interface])
                graph.links.add(link)
        return graph

    @property
    def nodes(self) -> ValuesView[Node]:
        return self.name_to_node.values()

    def add_node(self, node) -> None:
        self.name_to_node[node.name] = node

    def calculate_links(self) -> None:
        for node in self.nodes:
            for interface in node.interfaces:
                if not interface.neighbors:
                    continue
                link = interface.create_link_from_neighbors()
                self.links.add(link)

    def get_or_create_node(self, node_name: str) -> Node:
        node_name = Node.normalize_name(node_name)
        node = self.name_to_node.get(node_name)
        if node is None:
            node = Node(name=node_name)
            self.add_node(node)
        return node

    def dump(self) -> Dict[str, Any]:
        nodes = [{"id": node.id, "label": node.name} for node in self.nodes]

        edges = [
            {
                "from": link.first_interface.node.id,
                "to": link.second_interface.node.id,
                "title": str(link),
            }
            for link in self.links
            if link.is_point_to_point
        ]
        result = {
            "nodes": nodes,
            "edges": edges,
        }
        return result

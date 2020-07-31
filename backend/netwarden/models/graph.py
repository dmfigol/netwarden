from typing import Dict, TYPE_CHECKING, List, ValuesView, Any, Set
from netwarden.models.node import Node

if TYPE_CHECKING:
    from netwarden.models.link import Link


class Graph:
    def __init__(self):
        self.name_to_node: Dict[str, Node] = {}
        self.links: Set["Link"] = set()

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
        node = self.name_to_node.get(node_name)
        if node is None:
            node = Node(name=node_name)
            self.add_node(node)
        return node

    def dump(self) -> Dict[str, Any]:
        nodes = [
            {"id": node.id,
            "label": node.name}
            for node in self.nodes
        ]

        edges = [
            {
                "from": link.first_interface.node.id,
                "to": link.second_interface.node.id,
                "title": str(link)
            }
            for link in self.links
            if link.is_point_to_point
        ]
        result = {
            "nodes": nodes,
            "edges": edges,
        }
        return result

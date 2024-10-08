from time import sleep
from typing import Union
from random import choice

from src.server.chord.base_node import BaseNode
from network_utils import HEART_RESPONSE


class HeartBeatManager:
    def __init__(self):
        self.nodes: set[BaseNode] = set()

    def add_nodes(self, *nodes: Union[BaseNode, None]):
        for node in nodes:
            if node:
                self.nodes.add(node)

    def get_nodes(self):
        return list(self.nodes)

    def get_random_node(self):
        node = choice(list(self.nodes))

        return node

    def check_health(self, interval: float = 1):
        while True:
            temp_set: set[BaseNode] = set()
            for node in self.nodes:
                beat = node.heart()
                if beat is None or beat != HEART_RESPONSE:
                    temp_set.add(node)

            self.nodes = self.nodes - temp_set

            if len(self.nodes):
                node = self.get_random_node()

                first = node.successor()
                second = first and first.successor()

                self.add_nodes(first, second)

            sleep(interval)

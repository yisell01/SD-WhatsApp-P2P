import random
import sys
import time
from typing import Union
from .base_node import BaseNode
from ..hasher import generate_id
from network_utils import HEART_RESPONSE


class Finger:
    def __init__(self, i: int, m: int, k: int, node: Union[BaseNode, None] = None):
        m = 2**m
        k = 2**k
        self.node = node
        self.start = (i + k) % m
        self.end = (i + 2*k) % m
        

    def serialize(self):
        return {
            "start": self.start,
            "end": self.end,
            "node": self.node.serialize() if self.node else {}
        }


class Node(BaseNode):
    def __init__(self, ip: str, port: str, capacity: int):
        id = generate_id(f"{ip}:{port}", capacity)
        super().__init__(id, ip, port)

        self.fingers: list[Finger] = [Finger(id, capacity, k, None)
                                      for k in range(capacity)]
        self._predecessor: Union[BaseNode, None] = None

    @classmethod
    def create_network(cls, ip: str, port: str, network_capacity: int):
        node = cls(ip, port, network_capacity)

        for finger in node.fingers:
            finger.node = node
        node.set_predecessor(node)

        return node

    @staticmethod
    def _inside_interval(value: int, interval: tuple[int, int], inclusive: tuple[bool, bool] = (False, False)):
        low, up = interval

        if low == up:
            return value != low or any(inclusive)

        if low > up:
            low, up = up, low
            inclusive = (not inclusive[1], not inclusive[0])
            return not Node._inside_interval(value, (low, up), inclusive)

        inclusive_low, inclusive_up = inclusive

        def low_compare(
            v: int, l: int): return v >= l if inclusive_low else v > l
        def up_compare(
            v: int, u: int): return v <= u if inclusive_up else v < u

        return low_compare(value, low) and up_compare(value, up)

    def _alone(self):
        p = self == self.predecessor()
        s = p and self == self.successor()
        return s and all([finger.node and finger.node == self for finger in self.fingers])

    def network_capacity(self):
        return len(self.fingers)

    def successor(self):
        return self.fingers[0].node

    def set_successor(self, node: BaseNode):
        self.fingers[0].node = node

    def predecessor(self):
        return self._predecessor

    def set_predecessor(self, node: BaseNode):
        self._predecessor = node

    def closest_preceding_finger(self, id: int):
        node = self
        for finger in self.fingers[::-1]:
            if finger.node and self._inside_interval(finger.node.id, (self.id, id)):
                node = finger.node
                break

        return node

    def find_predecessor(self, id: int):
        node = self
        while True:
            successor = node.successor()
            if not successor:
                break

            if not self._inside_interval(id, (node.id, successor.id), (False, True)):
                closest = node.closest_preceding_finger(id)
                if not closest:
                    break

                node = closest
            else:
                break

        return node

    def find_successor(self, id: int):
        id_predecessor = self.find_predecessor(id)
        return id_predecessor and id_predecessor.successor()

    def join_network(self, node: BaseNode):
        id_successor = node.find_successor(self.id)
        if not id_successor:
            print("An error has ocurred! Try connecting through other node")
            return sys.exit(0)

        if id_successor.id == self.id:
            print("A node already exists with this id")
            return sys.exit(0)

        self.set_successor(id_successor)

    def notify(self, node: BaseNode):
        predecessor = self.predecessor()
        if (not predecessor) or self._inside_interval(node.id, (predecessor.id, self.id)):
            self.set_predecessor(node)


    def heart(self):
        return HEART_RESPONSE

    def _check_successor(self):
        successor = self.successor()
        if not (successor and successor.heart()):
            print(f"FINDING NEW SUCCESSOR OF {self}...")

            for finger in self.fingers[1:]:
                if finger.node:
                    if finger.node == successor:
                        finger.node = None
                    else:
                        finger.node.set_predecessor(self)
                        self.set_successor(finger.node)
                        break
            else:
                self.set_successor(self)
                self.set_predecessor(self)

            print(f"NEW SUCCESSOR OF {self}: {self.successor()}")

    def _stabilize(self):
        old_successor = self.successor()
        node = old_successor and old_successor.predecessor()

        if old_successor and node and self._inside_interval(node.id, (self.id, old_successor.id)):
            self.set_successor(node)

        new_successor = self.successor()
        return new_successor and new_successor.notify(self)

    def _fix_fingers(self, index: int):
        finger = self.fingers[index]
        finger.node = self.find_successor(finger.start)

        random_index = random.randint(1, self.network_capacity() - 1)
        if random_index != index:
            finger = self.fingers[random_index]
            finger.node = self.find_successor(finger.start)

    def keep_healthy(self, interval: float, *tasks):
        index = 1
        while True:
            time.sleep(interval)

            self._check_successor()
            self._stabilize()
            self._fix_fingers(index)

            for task in tasks:
                task()

            index += 1
            if index == self.network_capacity():
                index = 1

import asyncio
from threading import Thread
import time
import socket
from fastapi import FastAPI, Request
from uvicorn import Config, Server
from network_utils import inject_to_state, get_ip
from network_utils.ip_address import IPAddress
from . import NET_MASK, BROADCAST_PORT, BROADCAST_SERVER, BROADCAST_CLIENT


class IPBox:
    def __init__(self):
        self._ips: set[str] = set()

    def add(self, ip: str):
        self._ips.add(ip)

    def ips(self):
        return list(self._ips)


def broadcast_task(from_client: bool = False, timeout: float = 5, limit: int = 10, message_count: int = 3):
    port, message = BROADCAST_CLIENT if from_client else BROADCAST_SERVER
    ip = get_ip()

    app = FastAPI()
    ip_box = IPBox()

    inject_to_state(app, "ip_box", ip_box)

    def find(request: Request):
        ip_box: IPBox = request.state.ip_box
        client = request.client
        if client and len(ip_box.ips()) < limit:
            ip_box.add(client.host)

        return ""

    app.get("/find")(find)

    def _app_task():
        config = Config(app, host=ip, port=int(port))
        server = Server(config)
        asyncio.run(server.serve())
    app_task = Thread(target=_app_task, daemon=True)

    network_ip = IPAddress.from_string(ip) & NET_MASK
    broadcast_ip = network_ip | (~NET_MASK)

    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def _socket_task():
        for _ in range(message_count):
            server_socket.sendto(
                message, (broadcast_ip.to_string(), int(BROADCAST_PORT)))
            time.sleep(0.1)

        server_socket.close()
    socket_task = Thread(target=_socket_task, daemon=True)

    print("LOOKING FOR NETWORK NODES TO CONNECT...")

    app_task.start()
    socket_task.start()

    app_task.join(timeout)
    socket_task.join(timeout)

    ips = ip_box.ips()
    print("NODES FOUND:")
    for ip in ips:
        print(f"\tNODE AT {ip}")

    return ip_box.ips()

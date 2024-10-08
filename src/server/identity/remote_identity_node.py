from typing import Any
from src.server.identity.models import DataBaseUserModel
from ..chord.remote_node import RemoteNode as ChordRemoteNode
from ..chord.base_node import BaseNodeModel, BaseNode as ChordBaseNode
from .base_identity_node import BaseIdentityNode
from .models import DataBaseUserModel, DataUsersModel, DataMessagesModel


class RemoteIdentityNode(ChordRemoteNode, BaseIdentityNode):
    def _ensure_local(self, node: ChordRemoteNode) -> BaseIdentityNode:
        result_node: Any = super()._ensure_local(node)
        return result_node


    @classmethod
    def from_base_node(cls, node: ChordBaseNode):
        return cls(node.id, node.ip, node.port)

    def get_users(self, database_id: int = -1):
        try:
            response = self._manager.post(
                "/info/users", data={"database_id": database_id}, timeout=3)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                results: list = response.json()

                return [(result["nickname"], result["password"], result["ip"], result["port"]) for result in results]

            print("ERROR:", response.json()["detail"])

        return []

    def add_user(self, nickname: str, password: str,  ip: str, port: str, database_id: int):
        try:
            response = self._manager.put(
                "/user/add", data={"nickname": nickname, "password": password, "ip": ip, "port": port, "database_id": database_id}, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: bool = response.json()["success"]
                return result

            print("ERROR:", response.json()["detail"])

        return False

    def get_pasword(self, nickname: str, database_id: int):
        try:
            response = self._manager.post(
                f"/user/password/{nickname}", data={"database_id": database_id}, timeout=3)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: str = response.json()["password"]
                return result

            print("ERROR:", response.json()["detail"])

        return ""

    def delete_user(self, nickname: str, database_id: int):
        try:
            response = self._manager.delete(
                f"/user/delete/{nickname}", data={"database_id": database_id}, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: bool = response.json()["success"]
                return result

            print("ERROR:", response.json()["detail"])

        return False

    def update_user(self, nickname: str, ip: str, port: str, database_id: int):
        try:
            response = self._manager.put(
                "/user/update", data={'nickname': nickname, "ip": ip, "port": port, "database_id": database_id}, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: bool = response.json()["success"]
                return result

            print("ERROR:", response.json()["detail"])

        return False

    def get_ip_port(self, nickname: str, database_id: int):
        try:
            response = self._manager.post(
                f"/user/ip_port/{nickname}", data={"database_id": database_id}, timeout=3)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: str = response.json()["ip_port"]
                return result

            print("ERROR:", response.json()["detail"])

        return ""

    def nickname_identity_node(self, nickname: str, search_id: int = -1):
        try:
            response = self._manager.post(
                f"/info/identity/{nickname}", data={"search_id": search_id}, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                model = BaseNodeModel(**response.json())
                return self._ensure_local(self.__class__.from_base_model(model))

            print("ERROR:", response.json()["detail"])

    def search_identity_node(self, nickname: str):
        try:
            response = self._manager.get(
                f"/info/search_entity/{nickname}", timeout=3)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                model = BaseNodeModel(**response.json())
                return self._ensure_local(self.__class__.from_base_model(model))

            print("ERROR:", response.json()["detail"])


    def add_messages(self, source: str, destiny: str, value: str, database_id: int, id: int):
        try:
            response = self._manager.put("/messages/add",
                                         data={"source": source, "destiny": destiny, "value": value, "database_id": database_id, "id": id}, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: bool = response.json()["success"]
                return result

            print("ERROR:", response.json()["detail"])

        return False

    def search_messages_to(self, me: str, database_id: int):
        try:
            response = self._manager.post("/messages/to",
                                          data={"destiny": me, "database_id": database_id}, timeout=3)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                results: list[dict] = response.json()

                return [(result["user_id_from"], result["value"]) for result in results]

            print("ERROR:", response.json()["detail"])

        return []

    def delete_messages_to(self, me: str, database_id: int):
        try:
            response = self._manager.delete(f"/messages/delete/to/{me}",
                                            data={"database_id": database_id}, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result: bool = response.json()["success"]
                return result

            print("ERROR:", response.json()["detail"])

        return False


    def replicate(self, data: DataBaseUserModel, database_id: int):
        body = {
            "source": data.serialize(),
            "database_id": database_id
        }

        try:
            response = self._manager.put(
                "/info/replicate", data=body, timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code != 200:
                print("ERROR:", response.json()["detail"])

    def get_replication_data(self):
        try:
            response = self._manager.get("/info/replication_data", timeout=3)
        except Exception as e:
            print("ERROR", e)
        else:
            if response.status_code == 200:
                results: dict = response.json()

                users = [DataUsersModel(**result)
                         for result in results["users"]]
                messages = [DataMessagesModel(**result)
                            for result in results["messages"]]
                return DataBaseUserModel(users=users, messages=messages)


    def all_nodes(self, search_id: int = -1) -> list[BaseIdentityNode]:
        try:
            response = self._manager.get(f"/info/all/{search_id}", timeout=5)
        except Exception as e:
            print("ERROR:", e)
        else:
            if response.status_code == 200:
                result = response.json()
                return [self.__class__.from_base_model(BaseNodeModel(**node)) for node in result]

        return []

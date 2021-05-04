from typing import List


class Credentials:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    @classmethod
    def create_empty(cls):
        return cls(email="", password="")


class Proxy:
    def __init__(self, address: str, protocols: List[str]):
        self.address = address
        self.protocols = protocols

    @classmethod
    def create_empty(cls):
        return cls(address="", protocols=["http", "https"])

from typing import List


class Credentials:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    @classmethod
    def create_empty(cls):
        return cls(email="", password="")

    def __eq__(self, other):
        return self.email == other.email and self.password == other.password


class Proxy:
    # TODO: remove protocols (or set defaults)
    def __init__(self, address: str, protocols: List[str]):
        self.address = address
        self.protocols = protocols

    @classmethod
    def create_empty(cls):
        return cls(address="", protocols=["http", "https"])

    def __eq__(self, other):
        return self.address == other.address and self.protocols == other.protocols

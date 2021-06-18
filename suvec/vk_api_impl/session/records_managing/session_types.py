class Credentials:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    @classmethod
    def create_empty(cls):
        return cls(email="", password="")

    def __eq__(self, other):
        return self.email == other.email and self.password == other.password

    def __repr__(self):
        return f"creds: {self.email}, {self.password}"


class Proxy:
    def __init__(self, address: str):
        self.address = address

    @classmethod
    def create_empty(cls):
        return cls(address="")

    def __eq__(self, other):
        return self.address == other.address

    def __repr__(self):
        return f"proxy: {self.address}"

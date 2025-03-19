import json

from py.examples.command_gateway.enumeration import EnMessageType


class Header:
    __slots__ = ["MessageType"]

    def __init__(self, message_type: EnMessageType):
        self.MessageType: EnMessageType = message_type

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {"MessageType": self.MessageType.value}

    @classmethod
    def from_json(cls, json_str: str) -> 'Header':
        data = json.loads(json_str)
        return cls(EnMessageType(data["MessageType"]))

    def __str__(self) -> str:
        return f"MessageType: {self.MessageType}"


class BaseMessage():
    __slots__ = ["Header"]

    def __init__(self, header: 'Header'):
        self.Header: Header = header

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {"Header": self.Header.to_dict()}

    @classmethod
    def from_json(cls, json_str: str) -> 'BaseMessage':
        data = json.loads(json_str)
        return cls(Header.from_json(data["Header"]))

    def __str__(self) -> str:
        return f"Header: {self.Header}"

import json

from base_message import Header, BaseMessage
from py.examples.command_gateway.enumeration import EnMessageType


class Position:
    def __init__(self, X: float, Y: float) -> None:
        self.X: float = 0.0
        self.Y: float = 0.0

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {"X": self.X, "Y": self.Y}

    @classmethod
    def from_json(cls, json_str: str) -> 'Position':
        data = json.loads(json_str)
        return cls(data["X"], data["Y"])

    def __str__(self) -> str:
        return f"X: {self.X}, Y: {self.Y}"


class LivePosition(BaseMessage):
    __slots__ = ["Header", "Position", "IsPositionValid", "Speed", "Heading"]

    def __init__(self, X: float, Y: float, speed: float, heading: float, is_position_valid: bool) -> None:
        super().__init__(header=Header(EnMessageType.LivePosition))
        self.Position: Position = Position(X, Y)
        self.IsPositionValid: bool = is_position_valid
        self.Speed: float = speed
        self.Heading: float = heading

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["Position"] = self.Position.to_dict()
        data["IsPositionValid"] = self.IsPositionValid
        data["Speed"] = self.Speed
        data["Heading"] = self.Heading
        return data

    @classmethod
    def from_json(cls, json_str: str) -> 'LivePosition':
        data = json.loads(json_str)
        super().from_json(json_str)
        return cls(Position.from_json(json.dumps(data["Position"])),
                   data["Speed"], data["Heading"], data["IsPositionValid"])

    def __str__(self) -> str:
        return f"Position: {self.Position}, IsPositionValid: {self.IsPositionValid}, Speed: {self.Speed},\
            Heading: {self.Heading}"

import json


class TaskMessage:
    def __init__(self, task: str, message: str) -> None:
        self.task: str = task
        self.message: str = message

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {"task": self.task, "message": self.message}

    @classmethod
    def from_json(cls, json_str: str) -> 'TaskMessage':
        data = json.loads(json_str)
        return cls(**data)

    def __str__(self) -> str:
        return f"Task: {self.task}, Message: {self.message}"

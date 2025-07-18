from dataclasses import dataclass, field
from typing import Any, ClassVar

class BaseModel:
    def __init__(self, **data: Any):
        for k, v in data.items():
            setattr(self, k, v)

    @classmethod
    def schema(cls):
        return {}

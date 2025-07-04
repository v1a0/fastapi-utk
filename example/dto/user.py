from dataclasses import dataclass


@dataclass
class User:
    id: int
    age: int
    name: str
    is_active: bool

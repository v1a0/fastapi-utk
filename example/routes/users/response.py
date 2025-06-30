from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class User(BaseModel):
    id: int
    age: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
        alias_generator = to_camel

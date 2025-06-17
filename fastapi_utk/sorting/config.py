from pydantic import BaseModel


class SortingConfig(BaseModel):
    query_param_name: str = "sort"
    delimiter: str = ","
    is_negative_sorting_allowed: bool = True
    translate_as_camel_case: bool = True

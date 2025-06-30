import collections
import typing as tp
from dataclasses import dataclass

from fastapi import Query, params
from fastapi.exceptions import RequestValidationError
from pydantic.alias_generators import to_camel, to_snake


class SortingOption(tp.NamedTuple):
    field: str
    is_desc: bool

    @property
    def is_asc(self) -> bool:
        return not self.is_desc


@dataclass
class Sorting:
    """
    FastAPI Sorting Query Parameter Dependency Builder.

    Use this class to validate, normalize and convert query string parameters like:
    `?sort=-createdAt,name` into a typed list of `SortingOption`.

    Supports camelCase to snake_case transformation, negative sorting (`-field`),
    default values, and uniqueness enforcement.

    Attributes:
        query_param_name: The name of the query parameter to read from (default: "sort").
        delimiter: The separator used to split multiple values (default: ",").
        is_negative_sorting_allowed: If True, allows sorting by descending using `-field` (default: True).
        translate_as_camel_case: If True, converts incoming camelCase field names to snake_case (default: True).

    Example:
        >>> sorting = Sorting()
        ...
        >>> @app.get("/items")
        ... def list_items(
        ...     sort: Annotated[list[SortingOption], sorting.Depends(choices=["created_at", "name"])]
        ... ):
        ...     # your code

        A request like:
        >>> GET /items?sort=-createdAt,name

        Will produce:
        >>> sort
        ... [
        ...     SortingOption(field="created_at", is_desc=False),
        ...     SortingOption(field="name", is_desc=True),
        ... ]
    """

    query_param_name: str = "sort"
    delimiter: str = ","

    is_negative_sorting_allowed: bool = True
    translate_as_camel_case: bool = True

    raise_key_violation: tp.Callable[[str, str, list[str], str], tp.Never] | None = None
    raise_unique_violation: tp.Callable[[str, str, list[str], str], tp.Never] | None = (
        None
    )

    def __call__(
        self,
        choices: list[str],
        *,
        default: list[str] | None = None,
        delimiter: str | None = None,
        query_param_name: str | None = None,
        is_negative_sorting_allowed: bool | None = None,
        translate_as_camel_case: bool | None = None,
    ) -> tp.Callable[..., list[SortingOption]]:
        if default is None:
            default = []

        if delimiter is None:
            delimiter = self.delimiter

        if query_param_name is None:
            query_param_name = self.query_param_name

        if is_negative_sorting_allowed is None:
            is_negative_sorting_allowed = self.is_negative_sorting_allowed

        if translate_as_camel_case is None:
            translate_as_camel_case = self.translate_as_camel_case

        if translate_as_camel_case:
            choices = [to_camel(choice) for choice in choices]

        if is_negative_sorting_allowed:
            choices += [f"-{v}" for v in choices]

        def _sorting_dependency(
            sorting_query: str | None = Query(
                default=None,
                alias=tp.cast(str, query_param_name),
                example=tp.cast(str, delimiter).join(
                    choice for choice in choices if not choice.startswith("-")
                ),
            ),
        ) -> list[SortingOption]:
            if sorting_query is None:
                return [
                    SortingOption(field=key.lstrip("-"), is_desc=key.startswith("-"))
                    for key in default
                ]

            parsed_keys = collections.OrderedDict()

            for sorting_keys in sorting_query.strip().split(self.delimiter):
                is_desc = str(sorting_keys).startswith("-")
                key = str(sorting_keys).lstrip("-").strip()

                if not key:
                    continue

                if key not in choices:
                    if self.raise_key_violation:
                        self.raise_key_violation(
                            query_param_name, key, choices, sorting_query
                        )

                    raise RequestValidationError(
                        [
                            {
                                "loc": ["query", query_param_name],
                                "msg": f"Unknown sorting key '{key}', should be one of: {', '.join(choices)}",
                                "type": "value_error.enum",
                            },
                        ],
                    )

                if key in parsed_keys:
                    if self.raise_unique_violation:
                        self.raise_unique_violation(
                            query_param_name, key, choices, sorting_query
                        )

                    raise RequestValidationError(
                        [
                            {
                                "loc": ["query", query_param_name],
                                "msg": (
                                    f"Sorting keys must be unique — '{key}' is duplicated.",
                                ),
                                "type": "value_error.list.unique_items",
                            },
                        ],
                    )

                parsed_keys[key] = is_desc

            return [
                (
                    SortingOption(field=to_snake(key), is_desc=is_desc)
                    if translate_as_camel_case
                    else SortingOption(field=key, is_desc=is_desc)
                )
                for key, is_desc in parsed_keys.items()
            ]

        return _sorting_dependency

    def Depends(  # noqa
        self,
        choices: list[str],
        *,
        default: list[str] | None = None,
        delimiter: str | None = None,
        query_param_name: str | None = None,
        is_negative_sorting_allowed: bool | None = None,
        translate_as_camel_case: bool | None = None,
    ) -> params.Depends:
        sorting_dependency = self.__call__(
            choices=choices,
            default=default,
            delimiter=delimiter,
            query_param_name=query_param_name,
            is_negative_sorting_allowed=is_negative_sorting_allowed,
            translate_as_camel_case=translate_as_camel_case,
        )

        return params.Depends(sorting_dependency)

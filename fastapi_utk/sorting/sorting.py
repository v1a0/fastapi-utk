import typing as tp
from dataclasses import dataclass

from fastapi import Query, params
from fastapi.exceptions import RequestValidationError
from pydantic.alias_generators import to_camel, to_snake

from ..not_set import NotSet


class SortingOption(tp.NamedTuple):
    field: str
    is_asc: bool


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
        ...     SortingOption(field="created_at", is_asc=False),
        ...     SortingOption(field="name", is_asc=True),
        ... ]
    """

    query_param_name: str = "sort"
    delimiter: str = ","

    is_negative_sorting_allowed: bool = True
    translate_as_camel_case: bool = True

    def __call__(
        self,
        choices: list[str],
        *,
        default: list[str] | NotSet = NotSet.NOT_SET,
        delimiter: str | NotSet = NotSet.NOT_SET,
        query_param_name: str | NotSet = NotSet.NOT_SET,
        is_negative_sorting_allowed: bool | NotSet = NotSet.NOT_SET,
        translate_as_camel_case: bool | NotSet = NotSet.NOT_SET,
    ) -> tp.Callable[..., list[SortingOption]]:
        if isinstance(default, NotSet):
            default = []

        if isinstance(delimiter, NotSet):
            delimiter = self.delimiter

        if isinstance(query_param_name, NotSet):
            query_param_name = self.query_param_name

        if isinstance(is_negative_sorting_allowed, NotSet):
            is_negative_sorting_allowed = self.is_negative_sorting_allowed

        if isinstance(translate_as_camel_case, NotSet):
            translate_as_camel_case = self.translate_as_camel_case

        if is_negative_sorting_allowed:
            choices += [f"-{v}" for v in choices]

        if translate_as_camel_case:
            choices = [to_camel(choice) for choice in choices]

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
                    SortingOption(
                        field=option.lstrip("-"), is_asc=option.startswith("-")
                    )
                    for option in default
                ]

            parsed_options = {}

            for sorting_option in sorting_query.strip().split(self.delimiter):
                is_asc = not str(sorting_option).startswith("-")
                option = str(sorting_option).lstrip("-").strip()

                if not option:
                    continue

                if option not in choices:
                    raise RequestValidationError(
                        [
                            {
                                "loc": ["query", query_param_name],
                                "msg": f"Unknown sorting option '{option}', should be one of: {', '.join(choices)}",
                                "type": "value_error.enum",
                            },
                        ],
                    )

                if option in parsed_options:
                    raise RequestValidationError(
                        [
                            {
                                "loc": ["query", query_param_name],
                                "msg": (
                                    f"Sorting parameters must be unique — '{option}' is duplicated.",
                                ),
                                "type": "value_error.list.unique_items",
                            },
                        ],
                    )

                parsed_options[option] = is_asc

            return [
                (
                    SortingOption(field=to_snake(option), is_asc=is_asc)
                    if translate_as_camel_case
                    else SortingOption(field=option, is_asc=is_asc)
                )
                for option, is_asc in parsed_options.items()
            ]

        return _sorting_dependency

    def Depends(  # noqa
        self,
        choices: list[str],
        *,
        default: list[str] | NotSet = NotSet.NOT_SET,
        delimiter: str | NotSet = NotSet.NOT_SET,
        query_param_name: str | NotSet = NotSet.NOT_SET,
        is_negative_sorting_allowed: bool | NotSet = NotSet.NOT_SET,
        translate_as_camel_case: bool | NotSet = NotSet.NOT_SET,
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

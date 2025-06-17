import re

CAMEL_TO_SNAKE_PATTERN = re.compile(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def snake_to_camel_case(value: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        value (str): A snake_case string, e.g., "my_variable_name".

    Returns:
        str: The converted camelCase string, e.g., "myVariableName".

    Examples:
        >>> snake_to_camel_case("my_query_param") # "myQueryParam"
        >>> snake_to_camel_case("HTTP_response_code") # "httpResponseCode"
    """

    words = iter(value.split("_"))
    return next(words).lower() + "".join(word.capitalize() for word in words)


def camel_to_snake_case(value: str) -> str:
    """
    Convert a camelCase or PascalCase string to snake_case.

    This inserts underscores before uppercase transitions, then lowercases the result.

    Args:
        value (str): A camelCase or PascalCase string, e.g., "myVariableName".

    Returns:
        str: The resulting snake_case string, e.g., "my_variable_name".

    Examples:
        >>> camel_to_snake_case("myQueryParam") # "my_query_param"
        >>> camel_to_snake_case("HTTPRequest") # "http_request"
    """
    return CAMEL_TO_SNAKE_PATTERN.sub(r"_\1", value).lower()

# FastAPI Ultimate Toolkit

The most useful tools for any FastAPI project

<img width="400" src="https://raw.githubusercontent.com/v1a0/fastapi-utk/main/docs/images/logo.png" />

## Installation

```shell
pip install fastapi-utk
```

## Features

- Api
    - Pagination
        - Pagination
        - PaginationConfig
        - Paginator
        - Paginated
    - Sorting
        - Sorting
        - SortingOption
        - SortingConfig
    - Middlewares
        - CamelCaseQueryParamsMiddleware
    - OpenAPI
        - translate_query_params_snake_to_camel
- Utils
    - NotSet

# Use cases

[>>> CLICK THE LINK TO SEE EXAMPLE PROJECT <<<](./example)

## Pagination

### Example

```python
import typing as tp

from my_app import router
from my_app.response_models import User

from fastapi_utk import Paginated, Pagination, Paginator

pagination = Pagination()


@router.get("/users")
def get_users(
    paginator: tp.Annotated[Paginator, pagination.Depends()],
) -> Paginated[User]:
    total, users = get_users_from_db(..., limit=paginator.limit, offset=paginator.offset)

    return paginator(
        [
            User(
                id=user.id,
                age=user.age,
                name=user.name,
            )
            for user in users
        ],
        total=total,
    )
```

### Response

<img width="400" src="https://raw.githubusercontent.com/v1a0/fastapi-utk/refs/heads/main/docs/images/img-2.jpg" />

### Schema

<img width="400" src="https://raw.githubusercontent.com/v1a0/fastapi-utk/refs/heads/main/docs/images/img-1.jpg" />

### Extra

```python
import typing as tp

from fastapi_utk import Paginated, Pagination, Paginator

# Use Pagination class to specify global pagination configuration
pagination = Pagination()


# If for some routes you need non-default configuration, set it right in depends
@router.get("/foo")
def foo(
    paginator: tp.Annotated[
        Paginator,
        pagination.Depends(
            default_page=1,  # default page number if query param is not set
            default_page_size=10,  # default page size if query param is not set
            max_page_size=100,  # maximum page size
            url_page_query_param_name="fooPage",  # query param name to set a page number
            url_page_size_query_param_name="fooPageSize",
            # query param name to set page size, set `None` to disable this option
        )
    ]
) -> Paginated[MyModel]:  # use Paginated[...] to warp collection response
    # ...

    return paginator(..., total=...)  # total is used to calculate amount of pages

# /foo?fooPage=1&fooPageSize=100
```

----------------------------

## Sorting

### Example

```python
import typing as tp
from fastapi_utk import Sorting, SortingOption

from my_app import router
from my_app.response_models import User

sorting = Sorting()


@router.get("/users")
def get_users(
    sort_by: tp.Annotated[list[SortingOption], sorting.Depends(["age", "name"], default=["-age"])],
) -> list[User]:
    print(sort_by)
    # [
    #     SortingOption(field="baz", is_desc=False),
    #     SortingOption(field="baz_baz", is_desc=True),
    # ]
    
    total, users = get_users_from_db(..., _sort_by=sort_by)

    return [
        User(
            id=user.id,
            age=user.age,
            name=user.name,
        )
        for user in users
    ]
```

### Extra

```python
import typing as tp
from fastapi_utk import Sorting, SortingOption

# Use Sorting class to specify global pagination configuration
sorting = Sorting()


# If for some routes you need non-default configuration, set it right in depends
@router.get("/foo")
def foo(
    sort_by: tp.Annotated[
        list[SortingOption],
        sorting.Depends(
            choices=["bar", "baz_baz", "pop"],  # allowed sorting keys, for example `my.api/path?sort=bar,-pop`
            default=["-bar"],  # default sorting return (if not set by request params)
            delimiter=",",  # sorting keys delimiter
            url_query_param_name="sort"  # query param name to set sorting
        )
    ],
) -> ...:
    ...
    
# /foo?sort=baz,-barBaz
```

----------------------------

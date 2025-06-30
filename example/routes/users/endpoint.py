import typing as tp
from fastapi import Query

from fastapi_utk import Paginated, Pagination, Paginator, Sorting, SortingOption

from db.repo.user import UserRepo

from .router import router
from . import response


sorting = Sorting()
pagination = Pagination()


@router.get("/")
def get_users(
    paginator: tp.Annotated[Paginator, pagination.Depends()],
    sort_by: tp.Annotated[
        list[SortingOption],
        sorting.Depends(["id", "age", "name", "is_active"], default=["-id"]),
    ],
    age: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> Paginated[response.User]:
    print("paginator: ", paginator)
    print("sort_by: ", sort_by)

    total, users = UserRepo.get_users(
        age=age,
        is_active=is_active,
        _limit=paginator.limit,
        _offset=paginator.offset,
        _sort_by=sort_by,
    )

    return paginator(
        [
            response.User(
                id=user.id,
                age=user.age,
                name=user.name,
            )
            for user in users
        ],
        total=total,
    )

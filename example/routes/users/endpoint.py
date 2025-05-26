import typing as tp
from fastapi import Query

from fastapi_utk import Paginated, Pagination, Paginator
from fastapi_utk.not_set import NotSet

from db.repo.user import UserRepo

from .router import router
from . import response


pagination = Pagination()


@router.get("/")
def get_users(
    paginator: tp.Annotated[Paginator, pagination.Depends()],
    age: int | None = Query(default=None),
) -> Paginated[response.User]:
    total, users = UserRepo.get_users(
        age=age or NotSet.NOT_SET,
        _limit=paginator.limit,
        _offset=paginator.offset,
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

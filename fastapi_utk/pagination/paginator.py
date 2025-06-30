import typing as tp
from copy import deepcopy
from dataclasses import dataclass

from fastapi import Query, Request, params
from pydantic import BaseModel, HttpUrl
from starlette.datastructures import URL

from .response import Paginated, PaginationInfo

MIN_PAGE = 1
MIN_PAGE_SIZE = 1


@dataclass
class Paginator:
    page: int
    page_size: int

    url: URL | None = None
    url_page_param: str | None = None
    url_page_size_param: str | None = None

    def __call__[M: BaseModel](
        self,
        items: list[M],
        *,
        total: int | None = None,
    ) -> Paginated[M]:
        if total is None:
            total_pages = None
        else:
            total_pages = (total + self.page_size - 1) // self.page_size

        if (items_len := len(items)) < self.page_size:
            page_size = items_len
        else:
            page_size = self.page_size

        next_page_number = self.page + 1
        previous_page_number = self.page - 1

        if next_page_number < MIN_PAGE:
            next_page = self._get_page_url(MIN_PAGE)
        elif (total_pages is not None) and (next_page_number > total_pages):
            next_page = None
        else:
            next_page = self._get_page_url(next_page_number)

        if previous_page_number < MIN_PAGE:
            prev_page = None
        elif (total_pages is not None) and (previous_page_number > total_pages):
            prev_page = self._get_page_url(total_pages)
        else:
            prev_page = self._get_page_url(previous_page_number)

        return self.paginated_response(
            items=items,
            total=total,
            page=self.page,
            page_size=page_size,
            total_pages=total_pages,
            next_page=next_page,
            prev_page=prev_page,
        )

    @staticmethod
    def paginated_response[T: BaseModel](
        items: list[T],
        total: int | None,
        page: int,
        page_size: int,
        total_pages: int | None,
        next_page: HttpUrl | None,
        prev_page: HttpUrl | None,
    ) -> Paginated[T]:
        return Paginated(
            data=items,
            pagination=PaginationInfo(
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                next_page=next_page,
                prev_page=prev_page,
            ),
        )

    def _get_page_url(
        self,
        page_number: int,
    ) -> HttpUrl | None:
        if not self.url or not self.url_page_param or page_number < MIN_PAGE:
            return None

        url = deepcopy(self.url)

        if self.url_page_param:
            url = url.include_query_params(**{self.url_page_param: page_number})

        if self.url_page_size_param:
            url = url.include_query_params(**{self.url_page_size_param: self.page_size})

        return HttpUrl(str(url))

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass
class Pagination:
    default_page: int = 1
    default_page_size: int = 10
    max_page_size: int | None = 20
    url_page_param: str = "page"
    url_page_size_param: str = "pageSize"

    def __call__(
        self,
        *,
        default_page: int | None = None,
        default_page_size: int | None = None,
        max_page_size: int | None = None,
        url_page_param: str | None = None,
        url_page_size_param: str | None = None,
    ) -> tp.Callable[..., Paginator]:
        default_page = default_page or self.default_page
        default_page_size = default_page_size or self.default_page_size
        max_page_size = max_page_size or self.max_page_size
        url_page_param = url_page_param or self.url_page_param
        url_page_size_param = url_page_size_param or self.url_page_size_param

        if self.url_page_size_param:

            def _pagination_dependency(
                request: Request,
                page: int = Query(
                    default=default_page,
                    alias=url_page_param,
                    ge=MIN_PAGE,
                ),
                page_size: int = Query(
                    default=default_page_size,
                    alias=url_page_size_param,
                    ge=MIN_PAGE_SIZE,
                    le=max_page_size,
                ),
            ) -> Paginator:
                return Paginator(
                    page=page,
                    page_size=page_size,
                    url=request.url,
                    url_page_param=url_page_param,
                    url_page_size_param=url_page_size_param,
                )

        else:

            def _pagination_dependency(  # type: ignore[misc]
                request: Request,
                page: int = Query(
                    default=default_page,
                    alias=url_page_param,
                    ge=MIN_PAGE,
                    le=max_page_size,
                ),
            ) -> Paginator:
                return Paginator(
                    page=page,
                    page_size=default_page_size,
                    url=request.url,
                    url_page_param=url_page_param,
                )

        return _pagination_dependency

    def Depends(  # noqa
        self,
        *,
        default_page: int | None = None,
        default_page_size: int | None = None,
        max_page_size: int | None = None,
        url_page_param: str | None = None,
        url_page_size_param: str | None = None,
    ) -> params.Depends:
        pagination_dependency = self.__call__(
            default_page=default_page,
            default_page_size=default_page_size,
            max_page_size=max_page_size,
            url_page_param=url_page_param,
            url_page_size_param=url_page_size_param,
        )

        return params.Depends(pagination_dependency)

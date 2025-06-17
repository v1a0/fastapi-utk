import typing as tp
from copy import deepcopy
from dataclasses import dataclass

from fastapi import Depends, Query, Request
from pydantic import BaseModel, HttpUrl
from starlette.datastructures import URL

from .response import Paginated, PaginationInfo

MIN_PAGE = 1
MIN_PAGE_SIZE = 1


@dataclass
class Paginator:
    """
    Response data paginator

    Attributes:
        page (int): The current page number (1-based index).
        page_size (int): The number of items per page.
        url (URL | None): Original request URL for building pagination links.
        page_query_param_name (str | None): Name of the query parameter for page number (default: "page").
        page_size_query_param_name (str | None): Name of the query parameter for page size (default: "pageSize").
    """

    page: int
    page_size: int

    url: URL | None = None
    page_query_param_name: str | None = None
    page_size_query_param_name: str | None = None

    def __call__[M: BaseModel](
        self,
        items: list[M],
        *,
        total: int | None = None,
    ) -> Paginated[M]:
        """
        Build a paginated API response after items are fetched from the database.

        Args:
            items (list[M]): Fetched data for the current page.
            total (int | None): Optional total count of all matching items.

        Returns:
            Paginated[M]: Response with `data` and `pagination` metadata.
        """

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
            previous_page = None
        elif (total_pages is not None) and (previous_page_number > total_pages):
            previous_page = self._get_page_url(total_pages)
        else:
            previous_page = self._get_page_url(previous_page_number)

        return Paginated(
            data=items,
            pagination=PaginationInfo(
                total=total,
                page=self.page,
                page_size=page_size,
                total_pages=total_pages,
                next_page=next_page,
                prev_page=previous_page,
            ),
        )

    def _get_page_url(
        self,
        page_number: int,
    ) -> HttpUrl | None:
        if not self.url or not self.page_query_param_name or page_number < MIN_PAGE:
            return None

        url = deepcopy(self.url)

        if self.page_query_param_name:
            url = url.include_query_params(**{self.page_query_param_name: page_number})

        if self.page_size_query_param_name:
            url = url.include_query_params(
                **{self.page_size_query_param_name: self.page_size}
            )

        return HttpUrl(str(url))

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass
class Pagination:
    """
    FastAPI Pagination Dependency Builder.

    Constructs a FastAPI-compatible dependency for parsing pagination query parameters
    such as `page` and `pageSize`, returning a typed `Paginator` object. Designed for
    building consistent and reusable pagination logic across RESTful API endpoints.

    Features:
        - Enforces minimum and maximum page sizes
        - Injects current request URL into the paginator to support next/prev page links
        - Configurable default values and query parameter names
        - Supports integration with standardized `Paginated` response models

    Attributes:
        default_page (int): Default page number if not specified in the query (default: 1).
        default_page_size (int): Default number of items per page (default: 10).
        max_page_size (int | None): Maximum allowed items per page (default: 20).
        page_query_param_name (str): Query parameter name used for the page (default: "page").
        page_size_query_param_name (str): Query parameter name used for the page size (default: "pageSize").

    Example:
        >>> pagination = Pagination()
        ...
        >>> @app.get("/users")
        ... def list_users(
        ...     paginator: Annotated[Paginator, pagination.Depends()]
        ... ):
        ...     total, results = db.fetch(limit=paginator.limit, offset=paginator.offset)
        ...     return paginator(results, total=total)

        A request like:
        >>> GET /users?page=2&pageSize=10

        Will produce:
        >>> paginator.limit # 10
        >>> paginator.offset # 10
        >>> paginator(...) # Paginated response with metadata, including next/prev URLs
    """

    default_page: int = 1
    default_page_size: int = 10
    max_page_size: int | None = 20
    page_query_param_name: str = "page"
    page_size_query_param_name: str = "pageSize"

    def Depends(  # noqa
        self,
        *,
        default_page: int | None = None,
        default_page_size: int | None = None,
        max_page_size: int | None = None,
        page_query_param_name: str | None = None,
        page_size_query_param_name: str | None = None,
    ) -> tp.Callable[..., Paginator]:
        _paginator_dependency: tp.Callable[..., Paginator]

        default_page = default_page or self.default_page
        default_page_size = default_page_size or self.default_page_size
        max_page_size = max_page_size or self.max_page_size
        page_query_param_name = page_query_param_name or self.page_query_param_name
        page_size_query_param_name = (
            page_size_query_param_name or self.page_size_query_param_name
        )

        if self.page_size_query_param_name:

            def _paginator_dependency(
                request: Request,
                page: int = Query(
                    default=default_page,
                    alias=page_query_param_name,
                    ge=MIN_PAGE,
                ),
                page_size: int = Query(
                    default=default_page_size,
                    alias=page_size_query_param_name,
                    ge=MIN_PAGE_SIZE,
                    le=max_page_size,
                ),
            ) -> Paginator:
                return Paginator(
                    page=page,
                    page_size=page_size,
                    url=request.url,
                    page_query_param_name=page_query_param_name,
                    page_size_query_param_name=page_size_query_param_name,
                )

        else:

            def _paginator_dependency(
                request: Request,
                page: int = Query(
                    default=default_page,
                    alias=page_query_param_name,
                    ge=MIN_PAGE,
                    le=max_page_size,
                ),
            ) -> Paginator:
                return Paginator(
                    page=page,
                    page_size=default_page_size,
                    url=request.url,
                    page_query_param_name=page_query_param_name,
                )

        return tp.cast(tp.Callable[..., Paginator], Depends(_paginator_dependency))

import fastapi

from fastapi_utk.middleware import CamelCaseQueryParamsMiddleware
from fastapi_utk.openapi import translate_query_params_snake_to_camel
from routes.router import root_router


HOST = "127.0.0.1"
PORT = 8000


def create_app() -> fastapi.FastAPI:
    fastapi_app = fastapi.FastAPI()
    fastapi_app.include_router(root_router)

    # Swagger
    fastapi_app.openapi_schema = translate_query_params_snake_to_camel(
        fastapi_app.openapi(),
    )

    # Middlewares
    fastapi_app.add_middleware(CamelCaseQueryParamsMiddleware)

    return fastapi_app


if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run(
            app=create_app(),
            host=HOST,
            port=PORT,
        )
    except KeyboardInterrupt:
        ...

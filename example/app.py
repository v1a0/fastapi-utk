import fastapi
import uvicorn

from routes.router import root_router


HOST = "127.0.0.1"
PORT = "8000"


def create_app() -> fastapi.FastAPI:
    fastapi_app = fastapi.FastAPI()
    fastapi_app.include_router(root_router)

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

import uuid

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from trello.api.router import api_router
from trello.exceptions import NotFoundException
from trello.ssr import ssr_router

app = FastAPI()


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(_: Request, exc: NotFoundException):
    return JSONResponse(
        content={"message": exc.message},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.exception_handler(Exception)
async def internal_server_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        content={"message": "an unexpected error occurred"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = uuid.uuid4()
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["Trello-Request-Id"] = str(request_id)
    return response


app.include_router(ssr_router, prefix="")
app.include_router(api_router, prefix="/api")

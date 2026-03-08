from fastapi import FastAPI, Request, status
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


app.include_router(ssr_router, prefix="")
app.include_router(api_router, prefix="/api")

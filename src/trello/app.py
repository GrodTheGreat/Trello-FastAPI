from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from trello.api.router import api_router
from trello.exceptions import NotFoundException

app = FastAPI()


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(_: Request, exc: NotFoundException):
    return JSONResponse(
        content={"message": exc.message},
        status_code=status.HTTP_404_NOT_FOUND,
    )


app.include_router(api_router, prefix="/api")

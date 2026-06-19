from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.controller.routes import router
from app.model.database import Base, engine


VIEW_DIR = Path(__file__).resolve().parent / "view"


def validation_message(error: dict) -> str:
    field = str(error.get("loc", [""])[-1])
    error_type = error.get("type", "")
    context = error.get("ctx") or {}

    if field == "email":
        return "Podaj prawidłowy adres e-mail"
    if error_type == "missing":
        return "Pole jest wymagane"
    if error_type == "string_too_short":
        minimum = context.get("min_length")
        return f"Wartość musi mieć co najmniej {minimum} znaków"
    if error_type == "string_too_long":
        maximum = context.get("max_length")
        return f"Wartość może mieć maksymalnie {maximum} znaków"
    if error_type == "value_error":
        message = str(error.get("msg", "Nieprawidłowa wartość"))
        return message.removeprefix("Value error, ")
    return "Nieprawidłowe dane"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="RandomChoice", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "loc": error.get("loc", []),
            "msg": validation_message(error),
            "type": error.get("type", "value_error"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


app.mount("/static", StaticFiles(directory=VIEW_DIR), name="static")
app.include_router(router)

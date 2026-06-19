from pathlib import Path
from secrets import choice

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.controller.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.model import schemas
from app.model.database import get_db
from app.model.entities import Category, ChoiceHistory, Option, User


router = APIRouter()
VIEW_DIR = Path(__file__).resolve().parents[1] / "view"


def get_owned_category(category_id: int, user_id: int, db: Session) -> Category:
    category = db.scalar(
        select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono kategorii")
    return category


def get_owned_option(option_id: int, user_id: int, db: Session) -> Option:
    option = db.scalar(
        select(Option)
        .join(Category)
        .where(Option.id == option_id, Category.user_id == user_id)
    )
    if option is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono opcji")
    return option


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(VIEW_DIR / "index.html")


@router.post(
    "/api/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing_user = db.scalar(select(User).where(User.email == data.email))
    if existing_user is not None:
        raise HTTPException(
            status_code=409, detail="Użytkownik z tym adresem e-mail już istnieje"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Użytkownik z tym adresem e-mail już istnieje"
        )
    db.refresh(user)
    return user


@router.post("/api/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Nieprawidłowy adres e-mail lub hasło")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("/api/me", response_model=schemas.UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/api/categories", response_model=list[schemas.CategoryOut])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Category]:
    return list(
        db.scalars(
            select(Category)
            .where(Category.user_id == current_user.id)
            .order_by(Category.created_at.desc())
        )
    )


@router.post(
    "/api/categories",
    response_model=schemas.CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: schemas.CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    category = Category(name=data.name, user_id=current_user.id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete(
    "/api/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    category = get_owned_category(category_id, current_user.id, db)
    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/api/categories/{category_id}/options",
    response_model=list[schemas.OptionOut],
)
def list_options(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Option]:
    get_owned_category(category_id, current_user.id, db)
    return list(
        db.scalars(
            select(Option)
            .where(Option.category_id == category_id)
            .order_by(Option.created_at.desc())
        )
    )


@router.post(
    "/api/categories/{category_id}/options",
    response_model=schemas.OptionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_option(
    category_id: int,
    data: schemas.OptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Option:
    get_owned_category(category_id, current_user.id, db)
    option = Option(title=data.title, category_id=category_id)
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


@router.post(
    "/api/categories/{category_id}/random",
    response_model=schemas.RandomChoiceOut,
)
def make_random_choice(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.RandomChoiceOut:
    get_owned_category(category_id, current_user.id, db)
    active_options = list(
        db.scalars(
            select(Option).where(
                Option.category_id == category_id,
                Option.is_active.is_(True),
            )
        )
    )
    if not active_options:
        raise HTTPException(
            status_code=400,
            detail="W tej kategorii nie ma aktywnych opcji",
        )

    selected = choice(active_options)
    history = ChoiceHistory(
        user_id=current_user.id,
        category_id=category_id,
        selected_option_title=selected.title,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return schemas.RandomChoiceOut(
        selected_option_title=history.selected_option_title,
        history_id=history.id,
        created_at=history.created_at,
    )


@router.patch("/api/options/{option_id}/toggle", response_model=schemas.OptionOut)
def toggle_option(
    option_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Option:
    option = get_owned_option(option_id, current_user.id, db)
    option.is_active = not option.is_active
    db.commit()
    db.refresh(option)
    return option


@router.delete(
    "/api/options/{option_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_option(
    option_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    option = get_owned_option(option_id, current_user.id, db)
    db.delete(option)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/history", response_model=list[schemas.HistoryOut])
def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChoiceHistory]:
    return list(
        db.scalars(
            select(ChoiceHistory)
            .where(ChoiceHistory.user_id == current_user.id)
            .order_by(ChoiceHistory.created_at.desc())
        )
    )


@router.delete("/api/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    db.execute(
        delete(ChoiceHistory).where(ChoiceHistory.user_id == current_user.id)
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

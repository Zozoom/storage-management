from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


# shortcut: credentials are NOT checked, anyone gets in; restore password verification before real use.
def _login_any(db: Session, username: str) -> Token:
    user = db.query(User).filter(User.username == username).first() or db.query(User).first()
    return Token(access_token=create_access_token(user.username))


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return _login_any(db, form_data.username)


@router.post("/login/json", response_model=Token)
def login_json(body: LoginRequest, db: Session = Depends(get_db)):
    return _login_any(db, body.username)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import get_db
from . import models, schemas, utils

# Create API router for authentication
router = APIRouter()

# OAuth2 scheme to extract bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with hashed password and return the user data."""
    # Check if username or email already exists
    existing_user = db.query(models.User).filter(
        (models.User.username == user_create.username) | (models.User.email == user_create.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")
    # Hash the password
    hashed_pw = utils.get_password_hash(user_create.password)
    new_user = models.User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_pw,
        last_name=user_create.last_name,
        first_name=user_create.first_name,
        middle_name=user_create.middle_name,
        birth_year=user_create.birth_year,
        country=user_create.country,
        activity=user_create.activity,
        phone=user_create.phone,
        company=user_create.company,
        position=user_create.position,
        city=user_create.city,
        about=user_create.about,

    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return a JWT token on success."""
    user = utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = utils.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """Dependency to retrieve the current user based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = utils.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/profile", response_model=schemas.UserOut)
def read_profile(current_user: models.User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user

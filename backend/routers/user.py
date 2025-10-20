from fastapi import APIRouter
from schemas.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def list_users():
    return [{"id": 1, "name": "Test User"}]

@router.post("/")
def create_user(user: User):
    return {"message": "User created", "user": user}

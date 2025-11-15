from passlib.context import CryptContext

# bcrypt имеет лимит 72 байта на пароль
_MAX_BCRYPT_BYTES = 72
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_for_bcrypt(secret: str) -> str:
    data = secret.encode("utf-8")
    if len(data) > _MAX_BCRYPT_BYTES:
        data = data[:_MAX_BCRYPT_BYTES]
        return data.decode("utf-8", errors="ignore")
    return secret

def get_password_hash(password: str) -> str:
    """Хэширует пароль с учётом лимита bcrypt"""
    safe = _truncate_for_bcrypt(password)
    return pwd_context.hash(safe)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль с учётом лимита bcrypt"""
    safe = _truncate_for_bcrypt(plain_password)
    return pwd_context.verify(safe, hashed_password)

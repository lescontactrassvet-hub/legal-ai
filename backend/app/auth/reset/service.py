import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.auth.models import User  # модель пользователя из твоего auth/models.py
from app.auth.reset.models import PasswordResetToken, SupportRequest
from app.auth.reset.schemas import (
    ResetStartRequest,
    ResetStartResponse,
    ResetVerifyRequest,
    ResetVerifyResponse,
    ResetCompleteRequest,
    ResetCompleteResponse,
)
from app.auth.utils import get_password_hash  # уже используется для регистрации/логина


RESET_TOKEN_TTL_MINUTES = 15  # срок жизни одноразового токена (минуты)


def _find_user_for_reset(db: Session, email: str, phone: Optional[str]) -> Optional[User]:
    """
    Пытаемся найти пользователя по email или телефону.
    Если в модели User ещё нет поля phone, ищем только по email.
    """
    query = db.query(User)

    if hasattr(User, "phone") and phone:
        return query.filter((User.email == email) | (User.phone == phone)).first()

    return query.filter(User.email == email).first()


def start_reset(db: Session, payload: ResetStartRequest) -> ResetStartResponse:
    """
    1) Ищем пользователя по email/телефону.
    2) Если не нашли — создаём заявку оператору.
    3) Если нашли — создаём одноразовый токен.
    """
    user = _find_user_for_reset(db, payload.email, payload.phone)

    if not user:
        # создаём заявку оператору — пользователь не найден
        sr = SupportRequest(
            email=payload.email,
            phone=payload.phone,
            submitted_data=payload.model_dump_json(),
            status="new",
        )
        db.add(sr)
        db.commit()
        return ResetStartResponse(
            status="operator",
            token_sent=False,
            handed_to_operator=True,
        )

    # TODO: здесь можно будет добавить точное сравнение ФИО, года, страны и города
    # когда эти поля будут храниться в БД пользователя.

    # создаём одноразовый токен
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False,
    )
    db.add(reset_token)
    db.commit()

    # Здесь позже подключим реальную отправку email/SMS.
    # Сейчас это чисто backend-логика.
    #
    # send_email_reset_link(user.email, token)
    # if hasattr(user, "phone") and user.phone:
    #     send_sms_reset_code(user.phone, token)

    return ResetStartResponse(
        status="ok",
        token_sent=True,
        handed_to_operator=False,
    )


def verify_reset_token(db: Session, payload: ResetVerifyRequest) -> ResetVerifyResponse:
    token_obj = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == payload.token)
        .first()
    )

    if not token_obj:
        return ResetVerifyResponse(status="not_found", valid=False)

    if token_obj.used:
        return ResetVerifyResponse(status="used", valid=False)

    if token_obj.expires_at < datetime.utcnow():
        return ResetVerifyResponse(status="expired", valid=False)

    return ResetVerifyResponse(status="ok", valid=True)


def complete_reset(db: Session, payload: ResetCompleteRequest) -> ResetCompleteResponse:
    token_obj = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == payload.token)
        .first()
    )

    if not token_obj:
        return ResetCompleteResponse(status="token_not_found")

    if token_obj.used or token_obj.expires_at < datetime.utcnow():
        return ResetCompleteResponse(status="token_invalid")

    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user:
        return ResetCompleteResponse(status="user_not_found")

    # меняем логин + пароль
    user.username = payload.new_username
    user.hashed_password = get_password_hash(payload.new_password)

    token_obj.used = True

    db.commit()

    return ResetCompleteResponse(status="success")

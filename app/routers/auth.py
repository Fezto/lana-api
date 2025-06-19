# app/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.models import User, RefreshToken, PasswordReset, EmailVerification
from app.session import get_session
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import (
    LoginData,
    Token,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    LogoutRequest
)
from app.utils.hash import get_password_hash, verify_password
from app.utils.email import send_verification_email, send_reset_email
from app.utils.tokens import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="registerUser"                    # <- aquí
)
async def register(
    *,
    session: Session = Depends(get_session),
    user_in: UserCreate
):
    user = User(
        **user_in.model_dump(exclude_unset=True),
        password_hash=get_password_hash(user_in.password),
        email_verified=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    verification = EmailVerification(
        user_id=user.id,
        token=create_refresh_token({"sub": str(user.id)}),
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(verification)
    session.commit()

    await send_verification_email(user.email, verification.token)
    return user


@router.post(
    "/login",
    response_model=Token,
    operation_id="loginUser"                       # <- aquí
)
def login(
    *,
    session: Session = Depends(get_session),
    data: LoginData
):
    user = session.exec(select(User).where(User.email == data.email)).one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.email_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    db_rt = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session.add(db_rt)
    session.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=Token,
    operation_id="refreshTokens"                   # <- aquí
)
def refresh_tokens(
    *,
    session: Session = Depends(get_session),
    req: RefreshTokenRequest
):
    payload = decode_token(req.refresh_token)
    rt = session.exec(select(RefreshToken).where(RefreshToken.token == req.refresh_token)).one_or_none()
    if not rt or rt.revoked or rt.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(payload["sub"])
    access_token = create_access_token({"sub": str(user_id)})
    new_refresh = create_refresh_token({"sub": str(user_id)})

    rt.revoked = True
    session.add(rt)
    session.commit()

    nr = RefreshToken(
        user_id=user_id,
        token=new_refresh,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session.add(nr)
    session.commit()

    return Token(access_token=access_token, refresh_token=new_refresh)


@router.get(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    operation_id="verifyEmail"                     # <- aquí
)
def verify_email(
    *,
    session: Session = Depends(get_session),
    token: str = Query(...)
):
    ev = session.exec(select(EmailVerification).where(EmailVerification.token == token)).one_or_none()
    if not ev or ev.expires_at < datetime.utcnow() or ev.used:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = session.get(User, ev.user_id)
    user.email_verified = True
    ev.used = True
    session.add_all([user, ev])
    session.commit()
    return {"ok": True}


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    operation_id="forgotPassword"                  # <- aquí
)
async def forgot_password(
    *,
    session: Session = Depends(get_session),
    req: ForgotPasswordRequest
):
    user = session.exec(select(User).where(User.email == req.email)).one_or_none()
    if user:
        pr = PasswordReset(
            user_id=user.id,
            token=create_refresh_token({"sub": str(user.id)}),
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        session.add(pr)
        session.commit()
        await send_reset_email(user.email, pr.token)
    return {"ok": True}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    operation_id="resetPassword"                   # <- aquí
)
def reset_password(
    *,
    session: Session = Depends(get_session),
    req: ResetPasswordRequest
):
    pr = session.exec(select(PasswordReset).where(PasswordReset.token == req.token)).one_or_none()
    if not pr or pr.used or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = session.get(User, pr.user_id)
    user.password_hash = get_password_hash(req.password)
    pr.used = True
    session.add_all([user, pr])
    session.commit()
    return {"ok": True}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    operation_id="logoutUser"                      # <- aquí
)
def logout(
    *,
    session: Session = Depends(get_session),
    req: LogoutRequest
):
    rt = session.exec(select(RefreshToken).where(RefreshToken.token == req.refresh_token)).one_or_none()

    if not rt or rt.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )

    rt.revoked = True
    session.add(rt)
    session.commit()

    return {"ok": True}

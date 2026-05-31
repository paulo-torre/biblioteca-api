from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.models.user import UserResponse

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24h

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(user_id: str, email: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")
        username: str | None = payload.get("username")

        if user_id is None or email is None or username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    return UserResponse(id=user_id, email=email, username=username)
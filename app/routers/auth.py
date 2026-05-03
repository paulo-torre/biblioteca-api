import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import Depends, APIRouter, HTTPException
from app.database import supabase
from app.models.user import RegisterRequest, UserResponse, LoginRequest
from app.dependencies import get_current_user

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24 # 24h

@router.post("/register", response_model=UserResponse)
async def register(body: RegisterRequest):
    existing = supabase.table("users").select("id").eq("email", body.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")
    
    existing = supabase.table("users").select("id").eq("username", body.username).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Username já está em uso.")
    
    hashed_password = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt())

    result = supabase.table("users").insert({
        "email": body.email,
        "username": body.username,
        "password": hashed_password.decode("utf-8")
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao criar o usuário.")
    
    user = result.data[0]

    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"]
    )

@router.post("/login")
async def login(body: LoginRequest):
    result = supabase.table("users").select("*").eq("email", body.email).execute()
    
    if not result.data:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos.")
    
    user = result.data[0]

    password_matches = bcrypt.checkpw(
        body.password.encode("utf-8"),   # ksehblsehfballawdhb23b1l24
        user["password"].encode("utf-8") # 1234@muaythai
    )

    if not password_matches:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "username": user["username"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

@router.get("/teste")
async def teste(current_user = Depends(get_current_user)):
    return {"user_id": current_user["id"]}
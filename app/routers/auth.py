import os
import bcrypt
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models.user import RegisterRequest, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: RegisterRequest):
    existing = supabase.table("users").select("id").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")
    
    existing = supabase.table("users").select("id").eq("username", user.username).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Username já está em uso.")
    
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    result = supabase.table("users").insert({
        "email": user.email,
        "username": user.username,
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
async def login():
    pass
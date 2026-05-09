import bcrypt
from fastapi import APIRouter, HTTPException

from datetime import datetime, timezone

from app.database import supabase
from app.utils import generate_verification_code
from app.dependencies import create_access_token
from app.services.email import send_verification_email
from app.models.user import (
    RegisterRequest,
    LoginRequest,
    ResendVerificationRequest,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

router = APIRouter()

@router.post("/register")
async def register(body: RegisterRequest):
    existing = supabase.table("users").select("id").eq("email", body.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")
    
    existing = supabase.table("users").select("id").eq("username", body.username).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Username já está em uso.")
    
    hashed_password = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt())
    code, expires_at = generate_verification_code()

    result = supabase.table("users").insert({
        "email": body.email,
        "username": body.username,
        "password": hashed_password.decode("utf-8"),
        "email_verified": False,
        "verify_code": code,
        "verify_code_expires": expires_at.isoformat(),
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao criar o usuário.")
    
    send_verification_email(body.email, code)
    
    return {"message": "Conta criada. Verifique seu email para ativar."}

@router.post("/verify-email")
async def verify_email(body: VerifyEmailRequest):
    result = supabase.table("users").select("id, email, username, verify_code, verify_code_expires").eq("email", body.email).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    user = result.data[0]
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromisoformat(user["verify_code_expires"])

    if user["verify_code"] != body.code:
        raise HTTPException(status_code=400, detail="Código inválido.")

    if now > expires_at:
        raise HTTPException(status_code=400, detail="Código expirado.")
    
    supabase.table("users").update({
        "email_verified": True,
        "verify_code": None,
        "verify_code_expires": None
    }).eq("id", user["id"]).execute()
    
    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        username=user["username"]
    )

    return {"access_token": token, "token_type": "bearer"}

@router.post("/resend-verification")
async def resend_verification(body: ResendVerificationRequest):
    result = supabase.table("users").select(
        "id, email_verified"
    ).eq("email", body.email).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    user = result.data[0]

    if user["email_verified"]:
        raise HTTPException(status_code=400, detail="Email já verificado.")

    code, expires_at = generate_verification_code()

    supabase.table("users").update({
        "verify_code": code,
        "verify_code_expires": expires_at.isoformat(),
    }).eq("id", user["id"]).execute()

    send_verification_email(body.email, code)

    return {"message": "Novo código enviado."}

@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    pass

@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    pass

@router.post("/login")
async def login(body: LoginRequest):
    result = supabase.table("users").select("id, email, username, password, email_verified").eq("email", body.email).execute()
    
    if not result.data:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos.")
    
    user = result.data[0]

    if not user.get("email_verified"):
        raise HTTPException(status_code=403, detail="Email não verificado.")


    password_matches = bcrypt.checkpw(
        body.password.encode("utf-8"),
        user["password"].encode("utf-8")
    )

    if not password_matches:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        username=user["username"]
    )

    return {"access_token": token, "token_type": "bearer"}

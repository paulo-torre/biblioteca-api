import os
from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response

import app.services.email as email_service
from app.database import supabase
from app.dependencies import create_access_token, get_current_user
from app.models.user import (
    DeleteAccountRequest,
    EmailChangeRequest,
    PasswordChangeRequest,
    UserDTO,
    UsernameChangeRequest,
    UserResponse,
    VerifyEmailChangeRequest,
)
from app.utils import generate_verification_code

router = APIRouter()

@router.get("/me", response_model=UserDTO)
async def get_user_data(current_user: UserResponse=Depends(get_current_user)):
    # Dados do usuário
    user_result = supabase.table("users")\
        .select("id, email, username, created_at")\
        .eq("id", current_user.id)\
        .single()\
        .execute()

    saved_result = supabase.table("saved_books")\
        .select("id", count="exact")\
        .eq("user_id", current_user.id)\
        .execute()
    saved_count: int = saved_result.count if saved_result.count else 0

    opinions_result = supabase.table("book_opinions")\
        .select("id", count="exact")\
        .eq("user_id", current_user.id)\
        .execute()
    opinions_count: int = opinions_result.count if opinions_result.count else 0

    reviews_result = supabase.table("book_reviews")\
        .select("id", count="exact")\
        .eq("user_id", current_user.id)\
        .execute()
    reviews_count: int = reviews_result.count if reviews_result.count else 0

    user_data: dict = user_result.data
    user_data["stats"] = {
        "total_saved": saved_count,
        "total_opinions": opinions_count,
        "total_reviews": reviews_count
    }
    user_data["member_since"] = user_data.pop("created_at")

    return UserDTO(**user_data)


@router.put("/me/username")
async def username_change(body: UsernameChangeRequest, current_user: UserResponse = Depends(get_current_user)):
    existing = supabase.table("users").select("id").eq("username", body.username).execute()

    if existing.data:
        raise HTTPException(status_code=409, detail="Username já está em uso.")
    
    result = supabase.table("users").update({
        "username": body.username
    }).eq("id", current_user.id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    new_token = create_access_token(current_user.id, current_user.email, body.username)

    return {"access_token": new_token, "token_type": "bearer"}

@router.put("/me/email")
async def request_email_change(body: EmailChangeRequest, current_user: UserResponse = Depends(get_current_user)):

    existing = supabase.table("users").select("id").eq("email", body.new_email).execute()

    if existing.data:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    code, expires_at = generate_verification_code()

    supabase.table("users").update({
        "pending_email": body.new_email,
        "verify_code": code,
        "verify_code_expires": expires_at.isoformat(),
    }).eq("id", current_user.id).execute()

    email_service.send_email_change_email(body.new_email, code)

    return {"message": "Código enviado para o novo email."}

@router.put("/me/password")
async def request_password_change(body: PasswordChangeRequest, current_user: UserResponse = Depends(get_current_user)):
    result = supabase.table("users").select("password").eq("id", current_user.id).execute()
    user = result.data[0]

    password_matches = bcrypt.checkpw(
        body.password.encode("utf-8"),
        user["password"].encode("utf-8")
    )

    if not password_matches:
        raise HTTPException(status_code=401, detail="Senha inválida.")
    
    hashed_new_password = bcrypt.hashpw(body.new_password.encode("utf-8"), bcrypt.gensalt())

    result = supabase.table("users").update({
        "password": hashed_new_password.decode("utf-8")
    }).eq("id", current_user.id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao alterar senha.")
    
    return {"message": "Senha atualizada com sucesso."}

    

@router.post("/me/verify-email-change")
async def verify_email_change(body: VerifyEmailChangeRequest, current_user: UserResponse = Depends(get_current_user)):
    result = supabase.table("users").select(
        "pending_email, verify_code, verify_code_expires"
    ).eq("id", current_user.id).execute()

    user = result.data[0]
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromisoformat(user["verify_code_expires"])

    if user["verify_code"] != body.code:
        raise HTTPException(status_code=400, detail="Código inválido.")

    if now > expires_at:
        raise HTTPException(status_code=400, detail="Código expirado.")

    supabase.table("users").update({
        "email": user["pending_email"],
        "pending_email": None,
        "verify_code": None,
        "verify_code_expires": None,
    }).eq("id", current_user.id).execute()

    new_token = create_access_token(current_user.id, user["pending_email"], current_user.username)

    return {"access_token": new_token, "token_type": "bearer"}

@router.post("/me/request-delete")
async def request_user_delete(current_user: UserResponse = Depends(get_current_user)):
    code, expires_at = generate_verification_code()

    supabase.table("users").update({
        "verify_code": code,
        "verify_code_expires": expires_at.isoformat(),
    }).eq("id", current_user.id).execute()

    email_service.send_delete_confirmation(current_user.email, code)

    return {"message": "Código de confirmação enviado para o seu email."}

@router.delete("/me", status_code=204)
async def verify_user_deletion(body: DeleteAccountRequest, current_user: UserResponse = Depends(get_current_user)):
    result = supabase.table("users").select(
        "verify_code, verify_code_expires"
    ).eq("id", current_user.id).execute()

    user = result.data[0]
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromisoformat(user["verify_code_expires"])

    if user["verify_code"] != body.code:
        raise HTTPException(status_code=400, detail="Código inválido.")

    if now > expires_at:
        raise HTTPException(status_code=400, detail="Código expirado.")

    result = supabase.table("users").delete().eq("id", current_user.id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao deletar usuário.")

    return Response(status_code=204)
import re
from pydantic import BaseModel, EmailStr, field_validator

ALLOWED_SPECIAL_CHARS = r'@!#$%^&*()/'

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str):
        if not (8 <= len(v) <= 20):
            raise ValueError("A senha deve ter entre 8 e 20 caracteres.")
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("A senha deve conter ao menos uma letra.")
        if not re.search(r'[0-9]', v):
            raise ValueError("A senha deve conter ao menos um número.")
        if not re.search(r'[@!#$%^&*()/\\]', v):
            raise ValueError("A senha deve conter ao menos um caractere especial.")
        if re.search(r'[^a-zA-Z0-9@!#$%^&*()/\\]', v):
            raise ValueError("A senha contém caracteres não permitidos.")
        return v
    
    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("O username deve ter no mínimo 3 caracteres.")
        if not v.isalnum():
            raise ValueError("O username deve conter apenas letras e números.")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
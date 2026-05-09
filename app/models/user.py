from pydantic import BaseModel, EmailStr, field_validator

PASSWORD_SPECIAL_CHARS = set('_-.@!#$%&*')
USERNAME_SPECIAL_CHARS = set('-_.')

def validate_username(v: str) -> str:

    if len(v) < 3:
        raise ValueError("O username deve ter no mínimo 3 caracteres.")
    
    if not all(c in USERNAME_SPECIAL_CHARS or c.isdigit() or c.isalpha() for c in v):
        raise ValueError("O username contém caracteres inválidos.")

    return v

def validate_password(v: str) -> str:
    if not (8 <= len(v) <= 20):
        raise ValueError("A senha deve ter de 8 a 20 caracteres.")
    
    if not any(c.isalpha() for c in v):
        raise ValueError("A senha deve conter ao menos uma letra.")
    
    if not any(c.isdigit() for c in v):
        raise ValueError("A senha deve conter ao menos um número.")
    
    if not any(c in PASSWORD_SPECIAL_CHARS for c in v):
        raise ValueError("A senha deve conter ao menos um caractere especial.")
    
    if not all(c.isalpha() or c.isdigit() or c in PASSWORD_SPECIAL_CHARS for c in v):
        raise ValueError("A senha contém caracteres inválidos.")
    
    return v

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        return validate_password(v)
    
    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        return validate_username(v)

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
        
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class UsernameChangeRequest(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        return validate_username(v)

class PasswordChangeRequest(BaseModel):
    password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        return validate_password(v)
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        return validate_password(v)

class EmailChangeRequest(BaseModel):
    new_email: EmailStr

class VerifyEmailChangeRequest(BaseModel):
    code: str

class DeleteAccountRequest(BaseModel):
    code: str
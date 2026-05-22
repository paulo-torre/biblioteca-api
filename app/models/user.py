from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr

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

def validate_code(v: str) -> str:
    if len(v) != 6 or not v.isdigit():
        raise ValueError("O código deve conter exatamente 6 dígitos.")
    
    return v

ValidUsername = Annotated[str, AfterValidator(validate_username)]
ValidPassword = Annotated[str, AfterValidator(validate_password)]
ValidCode = Annotated[str, AfterValidator(validate_code)]

class RegisterRequest(BaseModel):
    email: EmailStr
    username: ValidUsername
    password: ValidPassword

class LoginRequest(BaseModel):
    email: EmailStr
    password: ValidPassword

class UserResponse(BaseModel):
    id: str
    email: str
    username: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: ValidCode

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class UsernameChangeRequest(BaseModel):
    username: ValidUsername

class PasswordChangeRequest(BaseModel):
    password: ValidPassword
    new_password: ValidPassword
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: ValidCode
    new_password: ValidPassword

class EmailChangeRequest(BaseModel):
    new_email: EmailStr

class VerifyEmailChangeRequest(BaseModel):
    code: ValidCode

class DeleteAccountRequest(BaseModel):
    code: ValidCode


class UserStats(BaseModel):
    total_saved:  int
    total_opinions: int
    total_reviews: int


class UserDTO(BaseModel):
    id: str
    email: str
    username: str
    stats: UserStats
    member_since: str
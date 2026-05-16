from pydantic import BaseModel, BeforeValidator
from typing import Annotated

VALID_SUFFIXES = {"W", "M", "A"}

def validate_opinion(v: str):
    if v not in ["liked", "loved", "disliked"]:
        raise ValueError("Opinião deve ser liked, loved ou disliked.")
    return v

def validate_rating(v: int):
    if v < 0 or v > 5 or v*2 % 1 != 0:
        raise ValueError("A avaliação deve ser um número inteiro entre 1 e 5.")
    return v

def validate_OLID(v: str) -> str:
    if not v.startswith("OL"):
        raise ValueError("OLID deve começar com 'OL'.")
    if len(v) < 4:
        raise ValueError("OLID inválido.")
    if v[-1] not in VALID_SUFFIXES:
        raise ValueError("OLID deve terminar com 'W', 'M' ou 'A'.")
    if not v[2:-1].isdigit():
        raise ValueError("OLID deve conter apenas números entre o 'OL' e o sufixo.")
    return v

ValidOpinion = Annotated[str, BeforeValidator(validate_opinion)]
ValidRating = Annotated[int, BeforeValidator(validate_rating)]
ValidOLID = Annotated[str, BeforeValidator(validate_OLID)]

class SearchBook(BaseModel):
    query: str

class SaveBook(BaseModel):
    book_id: ValidOLID

class DeleteBook(BaseModel):
    book_id: ValidOLID

class RateBook(BaseModel):
    book_id: ValidOLID
    rating: ValidRating
    
class EditRating(BaseModel):
    book_id: ValidOLID
    rating: ValidRating
    
class DeleteRating(BaseModel):
    book_id: ValidOLID
    
class ReviewBook(BaseModel):
    book_id: ValidOLID
    rating: ValidRating
    review: ValidOpinion
    
class EditReview(BaseModel):
    book_id: ValidOLID
    rating: ValidRating
    review: ValidOpinion

class DeleteReview(BaseModel):
    book_id: ValidOLID
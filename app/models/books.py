from typing import Annotated, Optional, Self

from pydantic import AfterValidator, BaseModel

from app.models.common import PaginatedResponse

VALID_SUFFIXES = {"W", "M", "A"}

def validate_opinion(v: str) -> str:
    if v not in ["liked", "loved", "disliked"]:
        raise ValueError("Opinião deve ser liked, loved ou disliked.")
    return v

def validate_rating(v: float) -> float:
    if v < 0 or v > 5 or v*2 % 1 != 0:
        raise ValueError("A avaliação deve estar entre 0 e 5 em múltiplos de 0.5.")
    return v

def validate_comment(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v) >= 500:
        raise ValueError("O comentário deve ter menos de 500 caracteres.")
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

ValidOpinion = Annotated[str, AfterValidator(validate_opinion)]
ValidRating = Annotated[float, AfterValidator(validate_rating)]
ValidComment = Annotated[Optional[str], AfterValidator(validate_comment)]
ValidOLID = Annotated[str, AfterValidator(validate_OLID)]


class OpineBook(BaseModel):
    book_id: ValidOLID
    opinion: ValidOpinion
    
class EditOpinion(BaseModel):
    book_id: ValidOLID
    opinion: ValidOpinion

class PushReview(BaseModel):
    book_id: ValidOLID
    rating: ValidRating
    comment: ValidComment = None

class SavedBookDTO(BaseModel):
    book_id: str
    saved_at: str

    @classmethod
    def from_db(cls, item: dict) -> Self:
        return cls(
            book_id=item["book_id"],
            saved_at=item["saved_at"]
        )


class OpinionDTO(BaseModel):
    book_id: str
    opinion: str
    opined_at: str

    @classmethod
    def from_db(cls, item: dict) -> Self:
        return cls(
            book_id=item["book_id"],
            opinion=item["opinion"],
            opined_at=item["opined_at"]
        )


class ReviewDTO(BaseModel):
    book_id: str
    rating: float
    comment: str | None
    username: str
    created_at: str

    @classmethod
    def from_db(cls, item: dict) -> Self:
        return cls(
            book_id=item["book_id"],
            rating=item["rating"],
            comment=item["comment"],
            username=item["users"]["username"],
            created_at=item["created_at"],
        )


class ViewHistoryDTO(BaseModel):
    book_id: str
    viewed_at: str

    @classmethod
    def from_db(cls, item: dict) -> Self:
        return cls(
            book_id=item["book_id"],
            viewed_at=item["viewed_at"]
        )

class ReviewSummary(BaseModel):
    average_rating: float | None
    rating_distribution: dict[float, int]


class PaginatedPublicReviewsResponse(PaginatedResponse[ReviewDTO]):
    summary: ReviewSummary
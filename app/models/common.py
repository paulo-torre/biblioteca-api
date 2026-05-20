from pydantic import BaseModel


class PaginatedResponse[T](BaseModel):
    data: list[T]
    page: int
    size: int
    total: int

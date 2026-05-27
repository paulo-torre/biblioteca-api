import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books, user

app = FastAPI(title="API da Biblioteca Virtual")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = [] # A definir!
else:
    origins = ["http://localhost:4200"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books

app = FastAPI(title="API da Biblioteca Virtual")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
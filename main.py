from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API da Biblioteca Virtual")

# Configuração de CORS - Essencial para o React conseguir falar com o Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

OPEN_LIBRARY_API_URL = "https://openlibrary.org"

# sobrescreve a função app.get pela search_books
@app.get("/api/books/search")
async def search_books(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="A string de busca não pode estar vazia.")

    # Fazendo a requisição assíncrona para a Open Library
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OPEN_LIBRARY_API_URL}/search.json", params={"q": query})
            response.raise_for_status() # Lança um erro se o status não for 200

            data = response.json()

            # Pegando apenas os 10 primeiros resultados para não sobrecarregar o front
            formatted_results = []
            for item in data.get("docs", [])[:10]:
                formatted_results.append({
                    "id": item.get("key"),
                    "title": item.get("title"),
                    "author": item.get("author_name", ["Autor Desconhecido"])[0],
                    "year": item.get("first_publish_year", "N/A"),
                    "cover_i": item.get("cover_i")
                })
            
            return {"results": formatted_results}
        
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
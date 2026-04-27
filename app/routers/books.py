import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()

OPEN_LIBRARY_API_URL = "https://openlibrary.org"

@router.get("/search")
async def search_books(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="A string de busca não pode estar vazia.")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OPEN_LIBRARY_API_URL}/search.json", params={"q": query})
            response.raise_for_status()
            data = response.json()

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
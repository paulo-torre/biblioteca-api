import httpx
from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user
from app.database import supabase
from datetime import datetime, timezone

router = APIRouter()

OPEN_LIBRARY_API_URL = "https://openlibrary.org"
VALID_RATINGS = {"liked", "loved", "disliked"}

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
        

@router.get("/saved")
async def get_saved_book(current_user = Depends(get_current_user)):
    
    #Retorna os livros salvos por um usuário após verificar a autenticação

    result = supabase.table("saved_books").select("book_id").eq("user_id", current_user["id"]).execute()

    return result.data


@router.post("/saved")
async def save_book(book_id: str, current_user = Depends(get_current_user)):

    #A Id deve ser no formato da Open Library, o OLID
    
    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            
            if response.status_code() != 200:                                           
                raise HTTPException(status_code=response.status_code(), detail="A Id do livro não foi encontrada.")
            

            existing = supabase.table("saved_books").select("user_id", "book_id").eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            if existing.data:
                raise HTTPException(status_code=409, detail="Livro já salvo por esse usuário.")


            result = supabase.table("saved_books").insert({
                "user_id": current_user["id"],
                "book_id": book_id,
                "saved_at": datetime.now(timezone.utc).isoformat()
            }).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao salvar livro.") 

            return "Livro salvo com sucesso."

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
        

@router.delete("/saved/{book_id}")
async def delete_book(book_id: str, current_user = Depends(get_current_user)):

    #Deleta livro com id book_id, em OLID, da tabela saved

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            
            if response.status_code() != 200:                                           
                raise HTTPException(status_code=response.status_code(), detail="A Id do livro não foi encontrada.")


            result = supabase.table("saved_books").delete().eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Livro não encontrado entre os salvos.") 

            return {"message": "Livro deletado com sucesso."}

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")


@router.get("/ratings")
async def get_ratings(current_user = Depends(get_current_user)):

    result = supabase.table("book_ratings").select("book_id, rating").eq("user_id", current_user["id"]).execute()

    return result.data


@router.post("/ratings")
async def rate_book(book_id: str, rating: str, current_user = Depends(get_current_user)):

    if rating not in VALID_RATINGS:
        raise HTTPException(status_code=400, detail="Avaliação inválida. Use liked, loved ou disliked.")


    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="ID do livro não foi encontrada.")


            existing = supabase.table("book_ratings").select("id").eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            #Se o usuário já avaliou o livro, roda um UPDATE
            if existing.data:
                result = supabase.table("book_ratings").update({
                    "rating": rating,
                    "rated_at": datetime.now(timezone.utc).isoformat()
                }).eq("user_id", current_user["id"]).eq("book_id", book_id).execute()
                
            #Senão, roda um INSERT
            else:
                result = supabase.table("book_ratings").insert({
                    "user_id": current_user["id"],
                    "book_id": book_id,
                    "rating": rating,
                    "saved_at": datetime.now(timezone.utc).isoformat()
                }).execute()


            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao salvar avaliação.")

            return result.data

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")


@router.delete("/ratings/{book_id}")
async def delete_rating(book_id: str, current_user = Depends(get_current_user)):

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="ID do livro não foi encontrada.")


            result = supabase.table("book_ratings").delete().eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            if not result.data:
                raise HTTPException(status_code=404, detail="Avaliação não encontrada.")


            return {"message": "Avaliação removida com sucesso."}

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
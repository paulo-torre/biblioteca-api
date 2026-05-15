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

    return {"data": result.data}


@router.post("/saved")
async def save_book(book_id: str, current_user = Depends(get_current_user)):

    #A Id deve ser no formato da Open Library, o OLID
    
    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            
            if response.status_code == 404:                                           
                raise HTTPException(status_code=response.status_code, detail="Livro não encontrado.")
            

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

            return {"message": "Livro salvo com sucesso."}

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
        

@router.delete("/saved/{book_id}")
async def delete_book(book_id: str, current_user = Depends(get_current_user)):

    #Deleta livro com id book_id, em OLID, da tabela saved
    
    result = supabase.table("saved_books").delete().eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Livro não encontrado entre os salvos.") 

    return {"message": "Livro deletado com sucesso."}


@router.get("/ratings")
async def get_ratings(current_user = Depends(get_current_user)):

    result = supabase.table("book_ratings").select("book_id, rating").eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao procurar livros avaliados.")

    return {"data": result.data}


@router.post("/ratings")
async def rate_book(book_id: str, rating: str, current_user = Depends(get_current_user)):

    if rating not in VALID_RATINGS:
        raise HTTPException(status_code=400, detail="Avaliação inválida. Use liked, loved ou disliked.")

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")


            existing = supabase.table("book_ratings").select("id").eq("book_id", book_id).eq("user_id", current_user["id"]).execute()

            if existing.data:
                raise HTTPException(status_code=500, detail="Você já avaliou este livro, tente editar a sua avaliação.")
            
            
            result = supabase.table("book_ratings").insert({
                "user_id": current_user["id"],
                "book_id": book_id,
                "rating": rating,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao salvar avaliação.")
            
            return {"message": "Avaliação salva com sucesso."}
        
        except httpx.RequestError:

            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
        

@router.put("/ratings")
async def edit_book_rating(book_id: str, rating: str, current_user = Depends(get_current_user)):

    if rating not in VALID_RATINGS:
        raise HTTPException(status_code=400, detail="Avaliação inválida. Use liked, loved ou disliked.")

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")


            existing = supabase.table("book_ratings").select("id").eq("book_id", book_id).eq("user_id", current_user["id"]).execute()

            if not existing.data:
                raise HTTPException(status_code=500, detail="Você ainda não avaliou este livro, tente adicionar uma avaliação.")
            
            
            result = supabase.table("book_ratings").update({
                "user_id": current_user["id"],
                "book_id": book_id,
                "rating": rating,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao salvar avaliação.")
            
            return {"message": "Avaliação editada com sucesso.", "data": result.data}
        
        except httpx.RequestError:

            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
        
@router.delete("/ratings/{book_id}")
async def delete_rating(book_id: str, current_user = Depends(get_current_user)):

    result = supabase.table("book_ratings").delete().eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")


    return {"message": "Avaliação removida com sucesso."}
        

@router.post("/reviews")
async def review_book(book_id: str, rating: float, review: str, current_user = Depends(get_current_user)):

    if rating < 0 or rating > 5 or rating*2 % 1 != 0:
        raise HTTPException(status_code=400, detail="Nota deve estar entre 0 e 5, em múltiplos de 0.5")

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")


            existing = supabase.table("book_reviews").select("id").eq("book_id", book_id).eq("user_id", current_user["id"]).execute()

            if existing.data:
                raise HTTPException(status_code=409, detail="Você já avaliou este livro, tente editar a sua avaliação.")
            
            
            result = supabase.table("book_reviews").insert({
                "user_id": current_user["id"],
                "book_id": book_id,
                "rating": rating,
                "comment": review,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao salvar review.")
            
            return {"data": result.data}
        
        except httpx.RequestError:

            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")


@router.put("/reviews")
async def edit_book_review(book_id: str, rating: int, review: str, current_user = Depends(get_current_user)):

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")


            existing = supabase.table("book_reviews").select("id").eq("book_id", book_id).eq("user_id", current_user["id"]).execute()

            if not existing.data:
                raise HTTPException(status_code=500, detail="Você ainda não avaliou este livro, tente adicionar uma avaliação.")
            
            
            result = supabase.table("book_reviews").update({
                "user_id": current_user["id"],
                "book_id": book_id,
                "rating": rating,
                "comment": review,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao editar review.")
            
            return {"data": result.data}
        
        except httpx.RequestError:

            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")


@router.delete("/reviews/{book_id}")
async def delete_review(book_id: str, current_user = Depends(get_current_user)):

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")


            result = supabase.table("book_reviews").delete().eq("user_id", current_user["id"]).eq("book_id", book_id).execute()

            if not result.data:
                raise HTTPException(status_code=404, detail="Review não encontrada.")


            return {"message": "Review removida com sucesso."}

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
        

@router.get("/reviews/{book_id}")
async def get_book_reviews(book_id: str):

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")
            

            result = supabase.table("book_reviews").select("book_id, user_id, rating, comment").eq("book_id", book_id).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erro ao procurar reviews do livro.")

            return {"data": result.data}
        
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")
        

@router.get("/reviews")
async def get_user_reviews(current_user = Depends(get_current_user)):

    result = supabase.table("book_reviews").select("user_id, book_id, rating, comment").eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao procurar reviews do livro.")

    return {"data": result.data}

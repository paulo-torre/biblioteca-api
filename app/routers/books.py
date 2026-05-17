import httpx
from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user
from app.database import supabase
from datetime import datetime, timezone
from app.models.books import (
    ValidOLID,
    SearchBook,
    SaveBook,
    UnsaveBook,
    OpineBook,
    EditOpinion,
    DeleteOpinion,
    PushReview,
    DeleteReview
)
from app.models.user import UserResponse

router = APIRouter()

OPEN_LIBRARY_API_URL = "https://openlibrary.org"

async def validate_book_exists(book_id: ValidOLID):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OPEN_LIBRARY_API_URL}/books/{book_id}.json")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Livro não encontrado.")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Erro ao se comunicar com a Open Library.")


@router.get("/search/{query}")
async def search_books(body: SearchBook):
    if not body.query:
        raise HTTPException(status_code=400, detail="A string de busca não pode estar vazia.")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OPEN_LIBRARY_API_URL}/search.json", params={"q": body.query})
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
async def get_saved_book(current_user: UserResponse = Depends(get_current_user)):
    
    result = supabase.table("saved_books").select("book_id").eq("user_id", current_user["id"]).execute()

    return {"data": result.data}


@router.post("/saved")
async def save_book(body: SaveBook, current_user: UserResponse = Depends(get_current_user)):

    await validate_book_exists(body.book_id)

    existing = supabase.table("saved_books").select("user_id", "book_id").eq("user_id", current_user["id"]).eq("book_id", body.book_id).execute()

    if existing.data:
        raise HTTPException(status_code=409, detail="Livro já salvo por esse usuário.")


    result = supabase.table("saved_books").insert({
        "user_id": current_user["id"],
        "book_id": body.book_id,
        "saved_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao salvar livro.") 

    return {"message": "Livro salvo com sucesso."}
        

@router.delete("/saved/{book_id}")
async def delete_book(body: UnsaveBook, current_user: UserResponse = Depends(get_current_user)):
    
    result = supabase.table("saved_books").delete().eq("user_id", current_user["id"]).eq("book_id", body.book_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Livro não encontrado entre os salvos.") 

    return {"message": "Livro deletado com sucesso."}


@router.get("/opinions")
async def get_opinions(current_user: UserResponse = Depends(get_current_user)):

    result = supabase.table("book_opinions").select("book_id, opinion").eq("user_id", current_user["id"]).execute()

    return {"data": result.data}


@router.post("/opinions")
async def opine_book(body: OpineBook, current_user: UserResponse = Depends(get_current_user)):

    await validate_book_exists(body.book_id)

    existing = supabase.table("book_opinions").select("id").eq("book_id", body.book_id).eq("user_id", current_user["id"]).execute()

    if existing.data:
        raise HTTPException(status_code=409, detail="Você já avaliou este livro, tente editar a sua avaliação.")
    
    
    result = supabase.table("book_opinions").insert({
        "user_id": current_user["id"],
        "book_id": body.book_id,
        "opinion": body.opinion,
        "opined_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao salvar avaliação.")
    
    return {"message": "Avaliação salva com sucesso."}   

@router.put("/opinions")
async def edit_book_opinion(body: EditOpinion, current_user: UserResponse = Depends(get_current_user)):

    await validate_book_exists(body.book_id)

    existing = supabase.table("book_opinions").select("id").eq("book_id", body.book_id).eq("user_id", current_user["id"]).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    
    
    result = supabase.table("book_opinions").update({
        "user_id": current_user["id"],
        "book_id": body.book_id,
        "opinion": body.opinion,
        "opined_at": datetime.now(timezone.utc).isoformat()
    }).eq("user_id", current_user["id"]).eq("book_id", body.book_id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao salvar avaliação.")
    
    return {"message": "Avaliação editada com sucesso.", "data": result.data}
        
@router.delete("/opinions/{book_id}")
async def delete_opinion(body: DeleteOpinion, current_user: UserResponse = Depends(get_current_user)):

    result = supabase.table("book_opinions").delete().eq("user_id", current_user["id"]).eq("book_id", body.book_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")


    return {"message": "Avaliação removida com sucesso."}
        

@router.post("/reviews")
async def review_book(body: PushReview, current_user: UserResponse = Depends(get_current_user)):

    await validate_book_exists(body.book_id)

    existing = supabase.table("book_reviews").select("id").eq("book_id", body.book_id).eq("user_id", current_user["id"]).execute()

    if existing.data:
        raise HTTPException(status_code=409, detail="Você já avaliou este livro, tente editar a sua avaliação.")
    
    
    result = supabase.table("book_reviews").insert({
        "user_id": current_user["id"],
        "book_id": body.book_id,
        "rating": body.rating,
        "comment": body.comment,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao salvar review.")
    
    return {"data": result.data}


@router.put("/reviews")
async def edit_book_review(body: PushReview, current_user: UserResponse = Depends(get_current_user)):

    await validate_book_exists(body.book_id)

    existing = supabase.table("book_reviews").select("id").eq("book_id", body.book_id).eq("user_id", current_user["id"]).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="Review não encontrada.")
    
    
    result = supabase.table("book_reviews").update({
        "user_id": current_user["id"],
        "book_id": body.book_id,
        "rating": body.rating,
        "comment": body.comment,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("user_id", current_user["id"]).eq("book_id", body.book_id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao editar review.")
    
    return {"data": result.data}


@router.delete("/reviews/{book_id}")
async def delete_review(body: DeleteReview, current_user: UserResponse = Depends(get_current_user)):

    result = supabase.table("book_reviews").delete().eq("user_id", current_user["id"]).eq("book_id", body.book_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Review não encontrada.")


    return {"message": "Review removida com sucesso."}
        

@router.get("/reviews/{book_id}")
async def get_book_reviews(book_id: ValidOLID):

    await validate_book_exists(book_id)

    result = supabase.table("book_reviews").select("book_id, user_id, rating, comment").eq("book_id", book_id).execute()

    return {"data": result.data}
        

@router.get("/reviews")
async def get_user_reviews(current_user: UserResponse = Depends(get_current_user)):

    result = supabase.table("book_reviews").select("user_id, book_id, rating, comment").eq("user_id", current_user["id"]).execute()

    return {"data": result.data}

import asyncio

from postgrest import APIResponse
from supabase import create_client, Client

from app.config import settings


supabase: Client = create_client(settings.db_url, settings.db_service_key)

async def run_query(query_fn) -> APIResponse:
    return await asyncio.to_thread(query_fn)
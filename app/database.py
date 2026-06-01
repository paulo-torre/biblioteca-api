import os
import asyncio

from postgrest import APIResponse
from postgrest.base_request_builder import SingleAPIResponse
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SUPABASE_URL = os.getenv("SUPABASE_URL" if ENVIRONMENT == "production" else "SUPABASE_DEVELOPMENT_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY" if ENVIRONMENT == "production" else "SUPABASE_DEVELOPMENT_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("Variáveis de ambiente do Supabase não configuradas.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

async def run_query(query_fn) -> APIResponse | SingleAPIResponse:
    return await asyncio.to_thread(query_fn)
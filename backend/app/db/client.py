import os
from supabase import create_client, Client

SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
SUPABASE_JWT_SECRET: str = os.environ.get("SUPABASE_JWT_SECRET")

if not all([SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET]):
    raise ValueError("One or more Supabase environment variables are missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

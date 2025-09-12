import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_interaction(user_id: str | None, user_input: dict, ai_response: str, metadata: dict = None):
    record = {
        "user_id": user_id,
        "user_input": user_input,
        "ai_response": ai_response,
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat()
    }
    res = supabase.table("ai_interactions").insert(record).execute()
    return res

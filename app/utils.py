import random
import string
from datetime import datetime, timedelta, timezone

def generate_verification_code() -> tuple[str, datetime]:
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    return code, expires_at
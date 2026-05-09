from app.database import supabase

_to_cleanup = []

def register_and_verify(client, email, username, password):
    client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": password
    })
    result = supabase.table("users").select("verify_code").eq("email", email).execute()
    code = result.data[0]["verify_code"]
    response = client.post("/api/auth/verify-email", json={"email": email, "code": code})

    if email not in _to_cleanup:
        _to_cleanup.append(email)

    return response.json()["access_token"]


def make_headers(token):
    return {"Authorization": f"Bearer {token}"}


def cleanup_user(email):
    supabase.table("users").delete().eq("email", email).execute()
    if email in _to_cleanup:
        try:
            _to_cleanup.remove(email)
        except ValueError:
            pass
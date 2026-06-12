from app.services.database import supabase

def test_verify_email_wrong_code(client, unverified_user):
    response = client.post("/api/auth/verify-email", json={
        "email": unverified_user["email"],
        "code": "000000"
    })
    assert response.status_code == 400

def test_verify_email_success(client, unverified_user):
    result = supabase.table("users").select("verify_code").eq("email", unverified_user["email"]).execute()
    code = result.data[0]["verify_code"]

    response = client.post("/api/auth/verify-email", json={
        "email": unverified_user["email"],
        "code": code
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
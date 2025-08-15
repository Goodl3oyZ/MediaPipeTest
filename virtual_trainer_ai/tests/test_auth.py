from backend.app import auth


def test_password_hash_roundtrip():
    pw = "secret"
    hashed = auth.hash_password(pw)
    assert auth.verify_password(pw, hashed)


def test_jwt_token_contains_claims():
    token = auth.create_access_token({"sub": "1", "role": "user"})
    payload = auth.decode_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "user"

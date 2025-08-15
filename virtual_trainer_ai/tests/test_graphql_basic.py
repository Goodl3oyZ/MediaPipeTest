import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db import Base, engine

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def graphql(query: str, variables: dict | None = None, headers: dict | None = None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post("/graphql", json=payload, headers=headers or {})


def test_register_and_login_flow():
    mutation = """
        mutation Register($email: String!, $password: String!) {
            register(input: {email: $email, password: $password}) { accessToken: access_token }
        }
    """
    email = "user@example.com"
    password = "pw12345"
    res = graphql(mutation, {"email": email, "password": password})
    token = res.json()["data"]["register"]["accessToken"]
    query_me = """
        query Me { me { email } }
    """
    res_me = graphql(query_me, headers={"Authorization": f"Bearer {token}"})
    assert res_me.json()["data"]["me"]["email"] == email

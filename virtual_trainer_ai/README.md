# Virtual Trainer AI

## Dev Quickstart

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

Open http://localhost:8000/graphql to interact with the API.

## Testing

```bash
pytest
```

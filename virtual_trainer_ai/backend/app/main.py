from fastapi import FastAPI

app = FastAPI(title="Virtual Trainer API")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}

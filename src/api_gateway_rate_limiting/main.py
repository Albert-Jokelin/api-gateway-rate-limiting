from fastapi import FastAPI

app = FastAPI(title="API Gateway with Contract-Based Rate Limiting")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

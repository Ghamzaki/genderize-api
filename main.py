from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime, timezone
from mangum import Mangum
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GENDERIZE_URL = "https://api.genderize.io"


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )


@app.get("/api/classify")
async def classify(name: str = Query(default=None)):
    # 400: missing or empty
    if name is None or name.strip() == "":
        raise HTTPException(status_code=400, detail="Missing or empty 'name' query parameter")

    # Call Genderize API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(GENDERIZE_URL, params={"name": name})
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=502, detail="Upstream API timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream API error: {e.response.status_code}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to contact upstream API")

    # Edge case: null gender or zero count
    if not data.get("gender") or not data.get("count"):
        raise HTTPException(status_code=422, detail="No prediction available for the provided name")

    probability = data["probability"]
    sample_size = data["count"]

    return {
        "status": "success",
        "data": {
            "name": name.lower(),
            "gender": data["gender"],
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": probability >= 0.7 and sample_size >= 100,
            "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    }


# Vercel serverless handler
handler = Mangum(app)
"""
main.py — FastAPI backend entry point for InfraSense.
Serves Karnataka district infrastructure and development intelligence API.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import StatusResponse
from routers import districts, indicators, rankings, clusters, compare, recommendations, eda

app = FastAPI(
    title="InfraSense API",
    description="Backend REST API for Karnataka District Development and Infrastructure Analytics.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard (local dev, static file preview, Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(districts.router)
app.include_router(indicators.router)
app.include_router(rankings.router)
app.include_router(clusters.router)
app.include_router(compare.router)
app.include_router(recommendations.router)
app.include_router(eda.router)


@app.get("/", response_model=StatusResponse, tags=["root"])
def root():
    """Health check and API metadata."""
    return StatusResponse(
        status="ok",
        project="InfraSense",
        version="1.0"
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

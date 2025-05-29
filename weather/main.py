
# main.py

import logging

from fastapi import FastAPI

from weather.api import router as weather_router
from weather.database import init_db

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
title = "Weather API"
description = (
    "Fetch current weather and 5-day forecasts, "
    "and manage saved locations via CRUD operations."
)
app = FastAPI(
    title=title,
    description=description,
    version="1.0.0",
)

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()

# Include weather router
description = "Endpoints to get current weather, 5-day forecast, and manage locations."
app.include_router(
    weather_router,
    prefix="",  # mount at root
    tags=["weather"],
)

# Optional health check at root
@app.get("/", summary="Health check")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Weather service is running."}

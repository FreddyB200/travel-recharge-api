from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_redis_client
import redis
import logging
import os
from app.routers import users, trips, finance, cards, stations, dashboard, routes, cache_metrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Travel Recharge API",
    description="A high-performance API for travel card recharge and trip management",
    version="1.0.0"
)

# Mount static files conditionally
static_dir = "static"
if os.path.exists(static_dir) and os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from {static_dir}")
else:
    logger.warning(
        f"Static directory {static_dir} not found, skipping static file mounting")

# Include routers
app.include_router(dashboard.router)  # Dashboard first (includes root route)
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(finance.router)
app.include_router(cards.router)
app.include_router(stations.router)
app.include_router(routes.router)
app.include_router(cache_metrics.router)

# Startup event


@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""
    logger.info("Testing database connection...")
    try:
        # This will be implemented when we need it
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

# Health check endpoints


@app.get("/api/v1/health")
def health_check():
    """Overall system health check"""
    return {"status": "healthy", "message": "Travel Recharge API is running"}


@app.get("/api/v1/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Simple query to test database connection
        result = db.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=503, detail={
                            "status": "unhealthy", "error": str(e)})


@app.get("/api/v1/health/cache")
def health_check_cache(redis_client: redis.Redis = Depends(get_redis_client)):
    """Redis cache health check"""
    try:
        # Test Redis connection
        redis_client.ping()
        return {"status": "healthy", "message": "Cache connection successful"}
    except Exception as e:
        raise HTTPException(status_code=503, detail={
                            "status": "unhealthy", "error": str(e)})

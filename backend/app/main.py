from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import news
from app.routes import admin
from app.routes import checker
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Hoax Detection News App API",
    description="API untuk deteksi hoaks berita Indonesia dengan auto-retraining",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(admin.router, tags=["Admin"])       # /api/admin/*
app.include_router(checker.router, tags=["Checker"])   # /api/checker/*


@app.get("/")
async def root():
    return {
        "message": "Hoax Detection News App API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "news": "/api/news - News CRUD operations",
            "admin": "/api/admin - Admin labeling & training management",
            "checker": "/api/checker - User hoax checking (NOT for training)",
            "docs": "/docs - Swagger UI documentation"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/stats")
async def get_system_stats():
    """Get overall system statistics"""
    try:
        from app.services.news_service import news_service
        from app.services.training_service import training_service

        news_stats = news_service.get_training_stats()
        training_status = training_service.get_training_queue_status()

        return {
            "news": news_stats,
            "training": {
                "pending": training_status.total_pending,
                "trained": training_status.total_trained,
                "threshold": training_status.threshold,
                "ready_for_training": training_status.ready_for_training
            }
        }
    except Exception as e:
        return {"error": str(e)}

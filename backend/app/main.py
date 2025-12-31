from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import news
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Hoax Detection News App API",
    description="API untuk deteksi hoaks berita Indonesia",
    version="1.0.0"
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
app.include_router(news.router, prefix="/api/news", tags=["news"])

@app.get("/")
async def root():
    return {
        "message": "Hoax Detection News App API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

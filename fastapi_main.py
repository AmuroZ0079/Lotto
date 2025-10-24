from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.line_webhook import router as line_router
from api.cron_service import router as cron_router

# Create FastAPI app
app = FastAPI(
    title="Thai Lottery API with LINE Bot",
    description="API for checking Thai lottery numbers with comprehensive prize information and LINE Bot integration",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(line_router, prefix="/line")
app.include_router(cron_router, prefix="/cron")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
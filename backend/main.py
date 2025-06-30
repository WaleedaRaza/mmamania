from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, get_db
from app.models import user, profile, fighter, fight, prediction, debate
from app.api import auth, users, fighters, fights, predictions, debates, ml

# Create database tables
user.Base.metadata.create_all(bind=engine)
profile.Base.metadata.create_all(bind=engine)
fighter.Base.metadata.create_all(bind=engine)
fight.Base.metadata.create_all(bind=engine)
prediction.Base.metadata.create_all(bind=engine)
debate.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FightHub - MMA Prediction & Community Platform API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(fighters.router, prefix="/fighters", tags=["Fighters"])
app.include_router(fights.router, prefix="/fights", tags=["Fights"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(debates.router, prefix="/debates", tags=["Debates"])
app.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FightHub API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
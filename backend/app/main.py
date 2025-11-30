from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, debates, fights, fighters, predictions, users
from .api import rankings, media_feed

app = FastAPI(
    title="FightHub API",
    description="API for FightHub - MMA Prediction and Analysis Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(fighters.router, prefix="/api/fighters", tags=["fighters"])
app.include_router(fights.router, prefix="/api/fights", tags=["fights"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(debates.router, prefix="/api/debates", tags=["debates"])
app.include_router(rankings.router, prefix="/api", tags=["rankings"])
app.include_router(media_feed.router, prefix="/api", tags=["media"])

@app.get("/")
async def root():
    return {"message": "Welcome to FightHub API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fighthub-api"} 
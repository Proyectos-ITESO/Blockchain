"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import auth, chat, websocket, verification

app = FastAPI(
    title="Encrypted Messaging API",
    description="Backend API for encrypted messaging with blockchain notarization",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(verification.router, prefix="/api", tags=["verification"])


@app.get("/")
async def root():
    return {
        "message": "Encrypted Messaging API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

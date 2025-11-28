"""
CodeLens AI - Main FastAPI application
AI-powered Intelligent Code Review Dashboard
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from routes.api import router as api_router
from database import db_manager
from middleware import RequestLoggingMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CodeLens AI backend...")
    
    # Connect to database
    await db_manager.connect()
    
    yield
    
    # Shutdown
    logger.info("Shutting down CodeLens AI backend...")
    await db_manager.disconnect()


# Create FastAPI application
app = FastAPI(
    title="CodeLens AI",
    description="AI-powered Intelligent Code Review Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://codelens-frontend-vfd3.onrender.com",  # Production frontend
        "https://codelens-frontend-vfd3.onrender.com/"  # With trailing slash
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CodeLens AI",
        "description": "AI-powered Intelligent Code Review Dashboard",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "report": "/api/report",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, init_db
from app.models import Base
from app.routers import auth, tasks, users
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Task Manager API",
    description="RESTful API for managing student tasks with JWT authentication",
    version="1.0.0",
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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {
        "message": "Welcome to Student Task Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
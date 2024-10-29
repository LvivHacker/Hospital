from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers here
from app.api import auth, users, patients, doctors, appointments

# Database connection and session handling
from app.db.base import Base, engine
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Management System",
    description="An API for managing hospital appointments, users, doctors, and patients.",
    version="1.0.0"
)

# CORS settings - adjust as per frontend requirements
origins = [
    "http://localhost:3000",  # React development server
    # Add other origins if needed for production or different environments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event to create database tables
@app.on_event("startup")
async def startup():
    # Create tables if they don’t exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers for each module
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(doctors.router, prefix="/api/doctors", tags=["Doctors"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])

# Root endpoint to verify if API is running
@app.get("/")
async def root():
    return {"message": "Welcome to the Hospital Management System API"}


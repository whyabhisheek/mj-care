from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic.config import Config
from alembic import command

from app.config import get_settings
from app.routers import appointments, auth, availability, availability_admin, bookings, chat, doctors, reports
from app.seed import seed_default_users


settings = get_settings()

app = FastAPI(
    title="MJ Care Backend",
    description="Backend API for the MJ Care wellness and appointment assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doctors.router)
app.include_router(auth.router)
app.include_router(availability.router)
app.include_router(availability_admin.router)
app.include_router(appointments.router)
app.include_router(bookings.router)
app.include_router(reports.router)
app.include_router(chat.router)


@app.on_event("startup")
def startup_seed_users() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    seed_default_users()


@app.get("/")
def health_check() -> dict[str, str]:
    return {"message": "MJ Care Backend Running"}

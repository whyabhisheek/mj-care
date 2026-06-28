from datetime import date, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.models.availability import Availability
from app.models.doctor import Doctor
from app.models.user import User
from app.utils.security import hash_password


DEFAULT_SLOTS = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]


def seed_default_availability(days_ahead: int = 14) -> None:
    with SessionLocal() as db:
        _seed_default_users(db)
        existing = db.scalar(select(Availability.id).limit(1))
        if existing is not None:
            return

        doctors = db.scalars(select(Doctor).order_by(Doctor.id)).all()
        if not doctors:
            return

        start_date = date.today()
        for day_offset in range(days_ahead):
            target_date = start_date + timedelta(days=day_offset)
            for doctor in doctors:
                for slot in DEFAULT_SLOTS:
                    db.add(
                        Availability(
                            doctor_id=doctor.id,
                            date=target_date,
                            slot=slot,
                            status="available",
                        )
                    )

        db.commit()


def seed_default_users() -> None:
    with SessionLocal() as db:
        _seed_default_users(db)


def _seed_default_users(db) -> None:
    if db.scalar(select(User.id).limit(1)) is not None:
        return

    db.add_all(
        [
            User(
                name="Admin",
                email="admin@xchange.com",
                password_hash=hash_password("Admin@12345"),
                role="admin",
            ),
            User(
                name="User",
                email="user@xchange.com",
                password_hash=hash_password("User@12345"),
                role="user",
            ),
        ]
    )
    db.commit()

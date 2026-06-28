"""add patient email to appointments

Revision ID: 20260627_0003
Revises: 20260627_0002
Create Date: 2026-06-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260627_0003"
down_revision: Union[str, None] = "20260627_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("appointments", sa.Column("patient_email", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_appointments_patient_email"), "appointments", ["patient_email"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_appointments_patient_email"), table_name="appointments")
    op.drop_column("appointments", "patient_email")

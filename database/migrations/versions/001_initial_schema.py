"""Create the complete EventPulse schema.

Revision ID: 001
Revises: None
"""
from alembic import op
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "backend"))
from app.core.database import Base
import app.models  # noqa: F401

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())

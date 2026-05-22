"""initial domain models

Revision ID: 20260521_01
Revises:
Create Date: 2026-05-21
"""

from alembic import op

from app.db import models as _models  # noqa: F401
from app.db.session import Base

revision = '20260521_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)

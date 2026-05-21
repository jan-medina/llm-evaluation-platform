from sqlalchemy import create_engine

from app.db.models import Base
from app.db import models as _models  # noqa: F401



def test_metadata_creation_with_sqlite() -> None:
    engine = create_engine('sqlite:///:memory:')

    Base.metadata.create_all(bind=engine)

    assert len(Base.metadata.tables) > 0

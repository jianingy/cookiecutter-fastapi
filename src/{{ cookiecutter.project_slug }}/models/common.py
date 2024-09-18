from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class RecordMixin:
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(True), index=True, nullable=False, default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(True), index=True, nullable=True, default=None, onupdate=func.now()
    )

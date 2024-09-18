from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from . import Base
from .common import RecordMixin


class AdminUser(Base, RecordMixin):
    __tablename__ = 'admin_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

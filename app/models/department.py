from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from app.core.base import Base

if TYPE_CHECKING:
    from .employee import Employee

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    parent: Mapped[Optional["Department"]] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[List["Department"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    employees: Mapped[List["Employee"]] = relationship(back_populates="department", cascade="all, delete-orphan")  # Строковая аннотация
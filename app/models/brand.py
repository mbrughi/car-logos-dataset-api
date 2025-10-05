from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base

class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    country: Mapped[str | None] = mapped_column(String(2), default=None)

    def __repr__(self) -> str:
        return f"<Brand {self.slug}>"

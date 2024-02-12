from sqlalchemy.orm import Mapped, mapped_column

from exchange_rates.db.base import Base


class Courses(Base):
    exchanger: Mapped[str] = mapped_column(primary_key=True)
    direction: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[float]

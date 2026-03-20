# ----- app/models.py -----
# SQLAlchemy ORM model for the URL table.
# This defines the actual PostgreSQL table structure.

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Index

from app.database import Base


class URL(Base):
    """
    Represents a shortened URL record in the database.

    Columns
    -------
    id          : Auto-incrementing primary key.
    long_url    : The original full URL the user wants to shorten.
    short_code  : The unique 6-char code (e.g. "abc123") used in the short link.
    created_at  : Timestamp of when the record was created.
    click_count : How many times the short link has been visited.
    expiry_date : (Optional) When this short link expires. NULL = never expires.
    """

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    long_url = Column(Text, nullable=False, index=True)       # indexed for duplicate lookup
    short_code = Column(String(10), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    click_count = Column(Integer, default=0, nullable=False)
    expiry_date = Column(DateTime, nullable=True)              # NULL = no expiry

    def __repr__(self):
        return f"<URL(id={self.id}, short_code='{self.short_code}', clicks={self.click_count})>"

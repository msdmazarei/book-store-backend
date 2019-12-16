from sqlalchemy import Column, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from db_session import PrimaryModel, Base


class BookOfMonth(Base,PrimaryModel):
    __tablename__ = 'book_of_month'

    total_income = Column(String)
    total_sale = Column(String)
    count = Column(String)
    title = Column(String)
    edition = Column(String)
    pub_year = Column(String)
    type = Column(String)
    language = Column(String)
    rate = Column(String)
    images = Column(ARRAY(UUID))
    genre = Column(ARRAY(UUID))
    files = Column(ARRAY(UUID))
    description = Column(String)
    duration = Column(String)
    isben = Column(String)
    pages = Column(String)
    size = Column(String)
    from_editor = Column(String)
    press = Column(UUID)


class BookOfWeek(Base,PrimaryModel):
    __tablename__ = 'book_of_week'

    total_income = Column(String)
    total_sale = Column(String)
    count = Column(String)
    title = Column(String)
    edition = Column(String)
    pub_year = Column(String)
    type = Column(String)
    language = Column(String)
    rate = Column(String)
    images = Column(ARRAY(UUID))
    genre = Column(ARRAY(UUID))
    files = Column(ARRAY(UUID))
    description = Column(String)
    duration = Column(String)
    isben = Column(String)
    pages = Column(String)
    size = Column(String)
    from_editor = Column(String)
    press = Column(UUID)

from sqlalchemy import Column, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from db_session import PrimaryModel, Base


class BestsellerBookOfMonth(Base,PrimaryModel):
    __tablename__ = 'bestseller_book_of_month'

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


class BestsellerBookOfWeek(Base,PrimaryModel):
    __tablename__ = 'bestseller_book_of_week'

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

class BestYearBook(Base,PrimaryModel):
    __tablename__ = 'best_book_of_year'

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


class LowsellerBookOfMonth(Base,PrimaryModel):
    __tablename__ = 'lowseller_book_of_month'

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


class LowsellerBookOfWeek(Base,PrimaryModel):
    __tablename__ = 'lowseller_book_of_week'

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

class TotalAnnualSale(Base):
    __tablename__ = 'total_annual_sales_by_month'
    sale_month = Column(String,primary_key=True)
    total_income = Column(String)

class AnnualSaleByPress(Base):
    __tablename__ = 'annual_sale_by_press'
    press_month = Column(String,primary_key=True)
    sale_month = Column(String)
    total_price = Column(String)
    value_occurrence = Column(String)
    press = Column(UUID)

class LastAudioBooks(Base,PrimaryModel):
    __tablename__ = 'last_popular_audio_books'

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

class LastPdfBooks(Base,PrimaryModel):
    __tablename__ = 'last_popular_pdf_books'

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

class WishBook(Base,PrimaryModel):
    __tablename__ = 'lowseller_book_of_week'

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

class LastEpubBooks(Base,PrimaryModel):
    __tablename__ = 'last_popular_epub_books'

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

class LastDVDBooks(Base,PrimaryModel):
    __tablename__ = 'last_popular_dvd_books'

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

class LastMsdBooks(Base,PrimaryModel):
    __tablename__ = 'last_popular_msd_books'

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

class LastHardCopyBooks(Base,PrimaryModel):
    __tablename__ = 'last_popular_hard_copy_books'

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
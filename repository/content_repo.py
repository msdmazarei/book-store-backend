from books.models import BookContent


def get_book_contents(book_id, db_session):
    return db_session.query(BookContent).filter(BookContent.book_id==book_id).all()
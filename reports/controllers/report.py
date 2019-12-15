from sqlalchemy import text

from log import logger, LogMsg


def book_of_month(db_session, username):
    query_string = (
        'SELECT total_income,total_sale,'
        'count,creation_date,modification_date,'
        'id,version,tags,creator,modifier,'
        'title,edition,pub_year,type,'
        'language,rate,images,genre,'
        'files,description,duration,'
        'isben,pages,size,from_editor,press'
        'FROM book_of_month;'
    )
    logger.info(LogMsg.START, username)
    result = db_session.execute(query_string)
    for item in result:
        print(item)
    return result

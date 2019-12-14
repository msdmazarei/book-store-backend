from log import logger, LogMsg


def book_of_month(db_session,username):
    logger.info(LogMsg.START,username)
    result = db_session.execute('''SELECT * FROM  book_of_month''')
    return result
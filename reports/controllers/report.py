from decimal import Decimal
from log import logger, LogMsg


def book_of_week(db_session, username):
    logger.info(LogMsg.START, username)

    query_string = (
        'SELECT total_income,total_sale,'
        'count,creation_date,modification_date,'
        'id,version,tags,creator,modifier,'
        'title,edition,pub_year,type,'
        'language,rate,images,genre,'
        'files,description,duration,'
        'isben,pages,size,from_editor,press '
        'FROM book_of_week;'
    )
    logger.debug(LogMsg.QUERY_OBJECT, query_string)
    result = db_session.execute(query_string)
    keys = ['total_income', 'total_sale', 'count', 'creation_date',
            'modification_date', 'id', 'version', 'tags', 'creator', 'modifier',
            'title', 'edition', 'pub_year', 'type', 'language', 'rate',
            'images', 'genre', 'files', 'description', 'duration', 'isben',
            'pages', 'size', 'from_editor', 'press']
    final_res = []
    for item in result:

        item_dict = dict(zip(keys, item))
        for key,value in item_dict.items():
            if isinstance(value,Decimal):
                value = float(value)
        final_res.append(item_dict)
    return final_res


def book_of_month(db_session, username):
    logger.info(LogMsg.START, username)

    query_string = (
        'SELECT total_income,total_sale,'
        'count,creation_date,modification_date,'
        'id,version,tags,creator,modifier,'
        'title,edition,pub_year,type,'
        'language,rate,images,genre,'
        'files,description,duration,'
        'isben,pages,size,from_editor,press '
        'FROM book_of_month;'
    )
    logger.debug(LogMsg.QUERY_OBJECT, query_string)
    result = db_session.execute(query_string)
    keys = ['total_income', 'total_sale', 'count', 'creation_date',
            'modification_date', 'id', 'version', 'tags', 'creator', 'modifier',
            'title', 'edition', 'pub_year', 'type', 'language', 'rate',
            'images', 'genre', 'files', 'description', 'duration', 'isben',
            'pages', 'size', 'from_editor', 'press']
    final_res = []
    for item in result:
        item_dict = dict(zip(keys, item))
        final_res.append(item)
    return final_res
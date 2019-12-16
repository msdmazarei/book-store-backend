from decimal import Decimal

from sqlalchemy.dialects.postgresql import UUID

from helper import model_to_dict
from log import logger, LogMsg
from reports.controllers.report_models import BestsellerBookOfMonth, BestsellerBookOfWeek


def book_of_week(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(BestsellerBookOfWeek).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_WEEK,final_res)
    logger.info(LogMsg.END)

    return final_res


def book_of_month(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(BestsellerBookOfMonth).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH,final_res)
    logger.info(LogMsg.END)

    return final_res
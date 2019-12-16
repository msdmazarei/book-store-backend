from decimal import Decimal

from sqlalchemy.dialects.postgresql import UUID

from enums import check_enum, BookTypes
from helper import model_to_dict
from log import logger, LogMsg
from reports.controllers.report_models import BestsellerBookOfMonth, \
    BestsellerBookOfWeek, LowsellerBookOfMonth, LowsellerBookOfWeek, \
    TotalAnnualSale, LastAudioBooks, LastDVDBooks, LastEpubBooks, \
    LastHardCopyBooks, LastMsdBooks, LastPdfBooks


def bestseller_book_of_week(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(BestsellerBookOfWeek).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_WEEK, final_res)
    logger.info(LogMsg.END)

    return final_res


def bestseller_book_of_month(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(BestsellerBookOfMonth).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res


def lowseller_book_of_month(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(LowsellerBookOfMonth).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res


def lowseller_book_of_week(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(LowsellerBookOfWeek).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res


def total_annual_sale_by_month(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(TotalAnnualSale).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res


def book_by_type(data, db_session, username):
    logger.info(LogMsg.START, username)
    type = data.get('type')
    check_enum(type, BookTypes)

    type_table = {
        'Pdf':LastPdfBooks,
        'Epub':LastEpubBooks,
        'Msd':LastMsdBooks,
        'DVD':LastDVDBooks,
        'Audio':LastAudioBooks,
        'Hard_Copy':LastHardCopyBooks
    }

    result = db_session.query(type_table[type]).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res

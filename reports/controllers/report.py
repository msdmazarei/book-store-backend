from decimal import Decimal

from sqlalchemy.dialects.postgresql import UUID

from enums import check_enum, BookTypes
from helper import model_to_dict
from log import logger, LogMsg
from reports.controllers.report_models import BestsellerBookOfMonth, \
    BestsellerBookOfWeek, LowsellerBookOfMonth, LowsellerBookOfWeek, \
    TotalAnnualSale, LastAudioBooks, LastDVDBooks, LastEpubBooks, \
    LastHardCopyBooks, LastMsdBooks, LastPdfBooks, BestYearBook, \
    AnnualSaleByPress
from repository.order_repo import order_count, invoice_count
from repository.user_repo import user_count


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
        'Pdf': LastPdfBooks,
        'Epub': LastEpubBooks,
        'Msd': LastMsdBooks,
        'DVD': LastDVDBooks,
        'Audio': LastAudioBooks,
        'Hard_Copy': LastHardCopyBooks
    }

    result = db_session.query(type_table[type]).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res


def best_book_of_year(db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(BestYearBook).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res


def user_performance(db_session, username):
    logger.info(LogMsg.START, username)
    result = {'user_count': user_count(db_session),
              'order_count': order_count(db_session),
              'invoice_count': invoice_count(db_session)}
    logger.debug(LogMsg.USER_PERFORMANCE_REPORT, result)
    logger.info(LogMsg.END)
    return result


def book_by_press(data,db_session,username):
    logger.info(LogMsg.START, username)

    press = data.get('press',[])
    if len(press) <1:
                result = db_session.query(AnnualSaleByPress).all()
    else:
        result = db_session.query(AnnualSaleByPress).filter(AnnualSaleByPress.press.in_(press)).all()
    final_res = list()
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.REPORT_BOOK_OF_MONTH, final_res)
    logger.info(LogMsg.END)

    return final_res
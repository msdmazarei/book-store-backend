from check_permission import get_user_permissions, has_permission, \
    validate_permissions_and_access
from enums import Permissions, Access_level
from financial_transactions.models import Transaction
from helper import Http_error, populate_basic_data, Http_response, model_to_dict
from infrastructure.schema_validator import schema_validate
from log import LogMsg, logger
from messages import Message
from repository.account_repo import get_account
from .constants import ADD_SCHEMA_PATH


def add(data, db_session, username=None):
    logger.info(LogMsg.START, username)

    # schema_validate(data,ADD_SCHEMA_PATH)
    if username is not None:
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session, 'TRANSACTION_ADD',
                                        access_level=Access_level.Premium)
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    account_id = data.get('account_id')
    logger.debug(LogMsg.GETTING_ACCOUNT_BY_ID, account_id)
    account = get_account(account_id, db_session)
    if account is None:
        logger.error(LogMsg.NOT_FOUND, {'account_id': account_id})
        raise Http_error(404, Message.NOT_FOUND)

    model_instance = Transaction()

    populate_basic_data(model_instance, username)
    model_instance.account_id = account_id
    model_instance.credit = data.get('credit')
    model_instance.debit = data.get('debit')
    model_instance.payment_details = data.get('payment_details')

    db_session.add(model_instance)
    logger.debug(LogMsg.TRANSACTION_ADDED, model_to_dict(model_instance))
    logger.info(LogMsg.END)

    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    if username is not None:
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session,
                                        'TRANSACTION_GET',
                                        access_level=Access_level.Premium)
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    return db_session.query(Transaction).filter(
        Transaction.account_id == id).order_by(
        Transaction.creation_date.desc()).all()


def get_all(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username is not None:
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session,
                                        'TRANSACTION_GET',
                                        access_level=Access_level.Premium)
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    result = Transaction.mongoquery(db_session.query(Transaction)).query(
        **data).end().all()
    res = []
    for item in result:
        res.append(model_to_dict(item))
    logger.info(LogMsg.END)
    return res


def delete(id, db_session, username=None):
    logger.info(LogMsg.START, username)
    if username is not None:
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session,
                                        'TRANSACTION_DELETE',
                                        access_level=Access_level.Premium)
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        db_session.query(Transaction).filter(Transaction.id == id).delete()
        logger.debug(LogMsg.TRANSACTION_DELETED, id)
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return Http_response(204, True)


def internal_add(data, db_session):
    logger.info(LogMsg.START)

    if data.get('credit') and data.get('debit'):
        logger.error(LogMsg.DATA_MISSING)
        raise Http_error(400, Message.CREDIT_DEBIT_ERROR)

    account_id = data.get('account_id')

    model_instance = Transaction()

    populate_basic_data(model_instance, None)
    model_instance.account_id = account_id
    model_instance.credit = data.get('credit')
    model_instance.debit = data.get('debit')
    model_instance.details = data.get('details')
    model_instance.payment_id = data.get('payment_id')

    db_session.add(model_instance)
    logger.debug(LogMsg.TRANSACTION_ADDED, model_to_dict(model_instance))
    logger.info(LogMsg.END)

    return model_instance

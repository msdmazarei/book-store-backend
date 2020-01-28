from uuid import uuid4

from sqlalchemy import and_

from book_rate.constants import ADD_SCHEMA_PATH, EDIT_SCHEMA_PATH
from book_rate.models import Rate
from books.controllers.book import get as get_book
from check_permission import get_user_permissions, has_permission, \
    validate_permissions_and_access
from enums import Permissions
from helper import Http_error, populate_basic_data, model_to_dict, \
    edit_basic_data
from infrastructure.schema_validator import schema_validate
from log import LogMsg, logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(db_session, data, username):
    logger.info(LogMsg.START, username)
    schema_validate(data, ADD_SCHEMA_PATH)

    user = check_user(username, db_session)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    book_id = data.get('book_id')
    book = get_book(book_id, db_session)
    if book is None:
        logger.error(LogMsg.NOT_FOUND, {'book_id': book_id})
        raise Http_error(400, Message.NOT_FOUND)

    logger.debug(LogMsg.RATE_CHECK,
                 {'book_id': book_id, 'person_id': user.person_id})
    rate = get(book_id, user.person_id, db_session)
    if rate:
        logger.debug(LogMsg.RATE_EXISTS,
                     {'book_id': book_id, 'person_id': user.person_id,
                      'rate': rate.rate})
        rate.rate = data.get('rate')
        logger.debug(LogMsg.RATE_CHANGED,
                     {'book_id': book_id, 'person_id': user.person_id,
                      'rate': rate.rate})

        return rate

    else:

        logger.debug(LogMsg.RATE_IS_NEW,
                     {'book_id': book_id, 'person_id': user.person_id})

        model_instance = Rate()
        populate_basic_data(model_instance, username, data.get('tags'))
        model_instance.person_id = user.person_id
        model_instance.rate = data.get('rate')
        model_instance.book_id = book_id
        db_session.add(model_instance)
        logger.debug(LogMsg.RATE_ADDED)
        logger.info(LogMsg.END)

        return model_instance


def get(book_id, person_id, db_session):
    logger.info(LogMsg.START)
    return db_session.query(Rate).filter(
        and_(Rate.book_id == book_id, Rate.person_id == person_id)).first()


def edit(id, data, db_session, username):
    logger.info(LogMsg.START)
    permission_data = {}
    schema_validate(data, EDIT_SCHEMA_PATH)

    user = check_user(username, db_session)

    logger.debug(LogMsg.RATE_CHECK, {'rate_id': id})
    model_instance = db_session.query(Rate).filter(Rate.id == id,
                                                   Rate.person_id == user.person_id).first()

    if model_instance:

        logger.debug(LogMsg.RATE_EXISTS, model_to_dict(model_instance))
    else:
        logger.error(LogMsg.RATE_NOT_EXISTS, {'rate_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    model_instance.rate = data.get('rate')
    edit_basic_data(model_instance, username, data.get('tags'))

    logger.debug(LogMsg.RATE_CHANGED, model_to_dict(model_instance))
    logger.info(LogMsg.END)

    return model_instance


def delete(id, db_session, username, **kwargs):
    logger.info(LogMsg.START)
    logger.debug(LogMsg.RATE_CHECK)
    model_instance = db_session.query(Rate).filter(Rate.id == id).first()
    if model_instance:
        logger.debug(LogMsg.RATE_EXISTS, model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.RATE_NOT_EXISTS, {'rate_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'RATE_DELETE',
                                    model=model_instance)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    try:
        db_session.delete(model_instance)
        logger.debug(LogMsg.RATE_DELETED, {'rate_id': id})

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return {}


def get_users_rate(book_id, person_id, db_session):
    logger.info(LogMsg.START)

    model_instance = get(book_id, person_id, db_session)
    if model_instance:
        logger.debug(LogMsg.RATE_EXISTS, model_to_dict(model_instance))
        return model_instance.rate
    else:
        logger.debug(LogMsg.RATE_NOT_EXISTS,
                     {'book_id': book_id, 'person_id': person_id})
        return 0.0

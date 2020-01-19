import hashlib
import json
import logging

from bottle import request, response
from sqlalchemy import and_

from book_library.models import Library
from books.controllers.book import book_to_dict
from check_permission import get_user_permissions, has_permission, \
    validate_permissions_and_access
from enums import Permissions
from helper import check_schema, populate_basic_data, Http_error, Http_response, \
    model_basic_dict, edit_basic_data
from infrastructure.schema_validator import schema_validate
from log import LogMsg, logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from repository.book_repo import get as get_book
from configs import ONLINE_BOOK_TYPES
from .constants import ADD_SCHEMA_PATH, EDIT_SCHEMA_PATH


def add(data, db_session, username=None):
    logging.info(LogMsg.START)
    # if username is not None:
    #     logger.debug(LogMsg.PERMISSION_CHECK, username)
    #     validate_permissions_and_access(username, db_session, 'LIBRARY_ADD')
    #     logger.debug(LogMsg.PERMISSION_VERIFIED)

    schema_validate(data, ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)
    book_id = data.get('book_id')
    person_id = data.get('person_id')
    logger.debug(LogMsg.LIBRARY_CHECK_BOOK_EXISTANCE,
                 {'book_id': book_id, 'person_id': person_id})
    if is_book_in_library(person_id, book_id, db_session):
        logger.error(LogMsg.ALREADY_IS_IN_LIBRARY, {'book_id': book_id})
        raise Http_error(409, Message.BOOK_IS_ALREADY_PURCHASED)

    book = get_book(book_id, db_session)
    if book.type.name not in ONLINE_BOOK_TYPES:
        logger.debug(LogMsg.LIBRARY_BOOK_TYPE_NOT_ADDABLE, book.type.name)
        return {}

    model_instance = Library()

    populate_basic_data(model_instance)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.person_id = person_id
    model_instance.book_id = book_id
    model_instance.progress = 0.00
    model_instance.status = {'status': 'buyed', 'reading_started': False,
                             'read_pages': 0, 'read_duration': 0.00,
                             'is_read': False}

    db_session.add(model_instance)
    logger.info(LogMsg.END)
    return model_instance


def get_personal_library(data, db_session, username):
    logger.info(LogMsg.START, username)
    #
    # logger.debug(LogMsg.PERMISSION_CHECK, username)
    # validate_permissions_and_access(username, db_session, 'LIBRARY_DELETE',{Permissions.IS_OWNER.value: True})
    # logger.debug(LogMsg.PERMISSION_VERIFIED)

    user = check_user(username, db_session)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    if data.get('filter') is None:
        data.update({'filter': {'person_id': user.person_id}})
    else:
        data['filter'].update({'person_id': user.person_id})

    logger.debug(LogMsg.LIBRARY_GET_PERSON_LIBRARY, username)

    result = Library.mongoquery(
        db_session.query(Library)).query(
        **data).end().all()

    logger.info(LogMsg.END)

    return lib_to_dictlist(result, db_session)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    model_instance = db_session.query(Library).filter(Library.id == id).first()

    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'library_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'LIBRARY_DELETE',
                                    model=model_instance)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    db_session.delete(model_instance)

    return Http_response(204, True)


def get_user_library(person_id, db_session, username=None):
    logger.info(LogMsg.START)

    if username is not None:
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session, 'LIBRARY_GET',
                                        prepare_permission_data(db_session,
                                                                username,
                                                                person_id=person_id))
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    result = db_session.query(Library).filter(
        Library.person_id == person_id).all()
    logger.info(LogMsg.END)
    return lib_to_dictlist(result, db_session)


def add_books_to_library(person_id, book_list, db_session, username=None):
    logger.info(LogMsg.START)
    if username is not None:
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session, 'LIBRARY_ADD')
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    result = []
    logger.debug(LogMsg.LIBRARY_ADD_BOOKS,
                 {'person_id': person_id, 'books': book_list})
    for book_id in book_list:
        if is_book_in_library(person_id, book_id, db_session):
            logger.error(LogMsg.ALREADY_IS_IN_LIBRARY, {'book_id': book_id})
            raise Http_error(409, Message.BOOK_IS_ALREADY_PURCHASED)

        lib_data = {'person_id': person_id, 'book_id': book_id}

        result.append(add(lib_data, db_session))
    logger.info(LogMsg.END)
    return result


def edit_status(id, data, db_session, username):
    logger.info(LogMsg.START, username)
    schema_validate(data, EDIT_SCHEMA_PATH)

    user = check_user(username, db_session)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    status = data.get('status', {})

    model_instance = db_session.query(Library).filter(Library.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, id)
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'LIBRARY_EDIT',
                                    model=model_instance)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    if status.get('reading_started'):
        model_instance.status['reading_started'] = status.get('reading_started')
    if status.get('read_pages'):
        model_instance.status['read_pages'] = status.get('read_pages')
    if status.get('read_duration'):
        model_instance.status['read_duration'] = status.get('read_duration')
    if status.get('status'):
        model_instance.status['status'] = status.get('status')
    if status.get('is_read'):
        model_instance.status['is_read'] = status.get('is_read')
    if 'progress' in data:
        model_instance.progress = data.get('progress')

    edit_basic_data(model_instance, username)
    logger.debug(LogMsg.MODEL_ALTERED, data)

    logger.info(LogMsg.END)

    return lib_to_dict(model_instance, db_session)


def lib_to_dictlist(library, db_session):
    result = []
    for item in library:
        res = model_basic_dict(item)
        item_dict = {
            'book_id': item.book_id,
            'person_id': item.person_id,
            'status': item.status,
            'progress': item.progress,
            'book': book_to_dict(db_session, item.book)
        }
        item_dict.update(res)
        result.append(item_dict)
    return result


def is_book_in_library(person_id, book_id, db_session):
    logger.info(LogMsg.START)
    result = db_session.query(Library).filter(
        and_(Library.person_id == person_id,
             Library.book_id == book_id)).first()

    if result is None:
        logger.debug(LogMsg.COLLECTION_BOOK_IS_NOT_IN_LIBRARY,
                     {'book_id': id, 'person_id': person_id})
        return False
    logger.info(LogMsg.END)
    return True


def books_are_in_lib(person_id, books, db_session):
    logger.debug(LogMsg.LIBRARY_CHECK_BOOK_EXISTANCE)
    for id in books:
        logger.debug(LogMsg.LIBRARY_CHECK_BOOK_EXISTANCE,
                     {'book_id': id, 'person_id': person_id})
        if not is_book_in_library(person_id, id, db_session):
            return False
    return True


def lib_to_dict(item, db_session):
    res = model_basic_dict(item)
    item_dict = {
        'book_id': item.book_id,
        'person_id': item.person_id,
        'status': item.status,
        'progress': item.progress,
        'book': book_to_dict(db_session, item.book)
    }
    item_dict.update(res)
    return item_dict


def head_user_library(db_session, username):
    logger.info(LogMsg.START)
    req = request
    user = check_user(username, db_session)
    logger.debug(LogMsg.USER_XISTS)
    person_id = user.person_id

    headers = request.headers

    result = db_session.query(Library).filter(
        Library.person_id == person_id).all()
    result_dict = lib_to_dictlist(result, db_session)
    result_str = json.dumps(result_dict).encode()
    result_hash = hashlib.md5(result_str).hexdigest()

    response.add_header('content_type', 'application/json')
    response.add_header('etag', result_hash)

    logger.info(LogMsg.END)
    return response


def prepare_permission_data(db_session, username, model_instance=None,
                            person_id=None):
    user = check_user(username, db_session)
    if person_id is not None and person_id == user.person_id:
        return {Permissions.IS_OWNER.value: True}
    elif model_instance is not None and model_instance.person_id == user.person_id:
        return {Permissions.IS_OWNER.value: True}
    return {}

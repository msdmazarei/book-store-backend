from books.controllers.book import book_to_dict
from books.models import BookContent
from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission, validate_permissions_and_access
from enums import Permissions, BookContentType, check_enums, check_enum
from helper import populate_basic_data, check_schema, Http_error, model_to_dict, \
    edit_basic_data, Http_response, model_basic_dict
from infrastructure.schema_validator import schema_validate
from log import logger, LogMsg
from messages import Message
from repository.book_repo import get as get_book
from ..constants import CONTENT_ADD_SCHEMA_PATH,CONTENT_EDIT_SCHEMA_PATH


def add(db_session, data, username):
    logger.info(LogMsg.START, username)
    schema_validate(data, CONTENT_ADD_SCHEMA_PATH)

    logger.debug(LogMsg.SCHEMA_CHECKED)

    book_id = data.get('book_id')
    type = data.get('type')

    logger.debug(LogMsg.ENUM_CHECK, {'BOOK_CONTENT_TYpe': type})
    check_enum(type, BookContentType)

    book = get_book(book_id, db_session)
    if not book:
        logger.error(LogMsg.NOT_FOUND, {'book_id': book_id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.CHECK_UNIQUE_EXISTANCE, data)
    content = get_be_data(book_id, type, db_session)
    if content is not None:
        logger.error(LogMsg.CONTENT_EXIST, data)
        raise Http_error(409, Message.ALREADY_EXISTS)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'BOOK_ADD',model=book)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    model_instance = BookContent()

    logger.debug(LogMsg.POPULATING_BASIC_DATA)

    populate_basic_data(model_instance, username, data.get('tags'))

    model_instance.content = data.get('content')
    model_instance.book_id = book_id
    model_instance.type = type
    model_instance.book_press = book.press

    db_session.add(model_instance)

    logger.info(LogMsg.END)

    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START, username)

    content = db_session.query(BookContent).filter(BookContent.id == id).first()
    if content is None:
        logger.error(LogMsg.NOT_FOUND, {'book_content_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    book = get_book(content.book_id, db_session)
    if book is None:
        logger.error(LogMsg.NOT_FOUND, {'book_id': content.book_id})
        raise Http_error(404, Message.NOT_FOUND)


    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'BOOK_CONTENT_GET',model=content)
    logger.debug(LogMsg.PERMISSION_VERIFIED)


    return content_to_dict(content, db_session)


def get_internal(id, db_session):
    return db_session.query(BookContent).filter(BookContent.id == id).first()



def get_by_celery_task(id, db_session):
    return db_session.query(BookContent).filter(BookContent.celery_task_id == id).first()


def get_be_data(book_id, type, db_session):
    return db_session.query(BookContent).filter(BookContent.book_id == book_id,
                                                BookContent.type == type).first()


def edit(id, data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data, CONTENT_EDIT_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    content = get_internal(id, db_session)
    if content is None:
        logger.error(LogMsg.NOT_FOUND, {'content_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    book = get_book(content.book_id, db_session)
    if 'book_id' in data.keys():
        book = get_book(data.get('book_id'), db_session)
        if book is None:
            logger.error(LogMsg.NOT_FOUND, {'book_id': data.get('book_id')})
            raise Http_error(404, Message.NOT_FOUND)



    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'BOOK_EDIT',model=content)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    try:
        for key, value in data.items():
            setattr(content, key, value)

        new_content = get_be_data(content.book_id, content.type, db_session)
        if new_content is not None and new_content.id != content.id:
            logger.error(LogMsg.BOOK_CONTENT_ALREADY_EXISTS,
                         content_to_dict(new_content, db_session))
            raise Http_error(409, Message.ALREADY_EXISTS)

        edit_basic_data(content, username, data.get('tags'))
        content.book_press = book.press
        if data.get('content') is not None:
            content.celery_task_id = None
            content.content_generated = False
    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(409, Message.ALREADY_EXISTS)
    logger.debug(LogMsg.EDIT_SUCCESS, model_to_dict(content))
    logger.info(LogMsg.END)
    return content_to_dict(content, db_session)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    content = get_internal(id, db_session)
    if content is None:
        logger.error(LogMsg.NOT_FOUND, {'content_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    book = get_book(content.book_id, db_session)


    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'BOOK_DELETE',
                                    model=content)
    logger.debug(LogMsg.PERMISSION_VERIFIED)


    try:
        db_session.delete(content)
        book.size=None

    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(409, Message.DELETE_FAILED)
    logger.debug(LogMsg.DELETE_SUCCESS, {'book_content_id': id})
    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_all(db_session, username, data=None):
    logger.info(LogMsg.START, username)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    permission_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    has_permit = has_permission_or_not(
        [Permissions.BOOK_ADD_PREMIUM, Permissions.BOOK_CONTENT_GET_PREMIUM,
         Permissions.BOOK_CONTENT_GET_PRESS],
        permissions, None, permission_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if data is None:
        result = db_session.query(BookContent).all()
    else:
        result = BookContent.mongoquery(db_session.query(BookContent)).query(
            **data).end().all()

    final_res = []
    for content in result:
        if has_permit or content.book_press in presses or content.creator == username:
            final_res.append(content_to_dict(content, db_session))


    return final_res


def content_to_dict(content, db_session):
    result = model_to_dict(content)
    attrs = {
        'book_id': content.book_id,
        'content': content.content,
        'book_press': content.book_press,
        'book': book_to_dict(db_session, content.book)

    }
    if isinstance(content.type, str):
        attrs.update({'type': content.type})
    else:
        attrs.update({'type': content.type.value})
    result.update(attrs)
    return result


def book_has_content(book_id,type,db_session):
    content =  db_session.query(BookContent).filter(BookContent.book_id == book_id,
                                                BookContent.type == type).first()
    if content is None:
        logger.debug(LogMsg.NOT_FOUND,{'content_of_book':book_id,'type':type})
        return False
    return content.id

def check_book_content(data,db_session,username):
    book_id = data.get('book_id')
    type = data.get('type')
    return {'content':book_has_content(book_id,type,db_session)}



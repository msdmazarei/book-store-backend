
from celery_works.celery_consumers import generate_book_content
from celery.result import AsyncResult

from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission
from enums import Permissions
from helper import model_to_dict, Http_error, check_schema
from books.controllers.book_content import get_internal as get_content
from books.controllers.content_path_finder import return_content_full_path
from log import logger, LogMsg
from messages import Message
from repository.book_repo import get as get_book


def generate_book( data,db_session,username):
    logger.info(LogMsg.START,username)

    check_schema(['content_id'],data.keys())

    logger.debug(LogMsg.SCHEMA_CHECKED)

    content_id = data.get('content_id')
    content = get_content(content_id, db_session)
    if content is None:
        logger.error(LogMsg.NOT_FOUND,{'book_content_id':content_id})
        raise Http_error(404,Message.NOT_FOUND)

    book = get_book(content.book_id,db_session)
    if book is None:
        logger.error(LogMsg.NOT_FOUND,{'book_id':content.book_id})
        raise Http_error(404,Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    permissions, presses = get_user_permissions(username, db_session)
    per_data ={}
    if book.creator==username:
        per_data.update({Permissions.IS_OWNER.value:True})

    has_permit = has_permission_or_not([Permissions.BOOK_CONTENT_ADD_PREMIUM],
                                       permissions,None,per_data)
    if not has_permit:
        if book.press in presses :
            has_permission([Permissions.BOOK_CONTENT_ADD_PRESS], permissions)
        else:
            logger.error(LogMsg.PERMISSION_DENIED)
            raise Http_error(403, Message.ACCESS_DENIED)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if content.content_generated:
        logger.error(LogMsg.CONTENT_ALREADY_GENERATED)
        raise Http_error(409,Message.ALREADY_EXISTS)

    elif content.celery_task_id is not None:
        status = check_status(content.celery_task_id)
        if status=='SUCCESS':
            content.content_generated = True
            logger.error(LogMsg.CONTENT_ALREADY_GENERATED)
            raise Http_error(409,Message.ALREADY_EXISTS)

    content = return_content_full_path(data)

    result = generate_book_content.apply_async(args=[content],
                                  routing_key='book_generate')
    print(result.task_id)
    # result.get()
    return {'inquiry_id':result.task_id}

def check_status(id):
    result = AsyncResult(id)
    return {'inquiry_result':result.status}



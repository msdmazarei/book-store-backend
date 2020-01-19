
from celery_works.celery_consumers import generate_book_content
from celery.result import AsyncResult

from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission, validate_permissions_and_access
from enums import Permissions
from helper import  Http_error
from books.controllers.book_content import get_internal as get_content
from books.controllers.content_path_finder import return_content_full_path
from infrastructure.schema_validator import schema_validate
from log import logger, LogMsg
from messages import Message
from repository.book_repo import get as get_book
from .constants import GENERATE_BOOK_SCHEMA_PATH


def generate_book( data,db_session,username):
    logger.info(LogMsg.START,username)

    schema_validate(data,GENERATE_BOOK_SCHEMA_PATH)
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
    per_data ={}
    if book.creator==username:
        per_data.update({Permissions.IS_OWNER.value:True})

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session, 'BOOK_CONTENT_ADD',
                                    model=content)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    if content.content_generated:
        logger.error(LogMsg.CONTENT_ALREADY_GENERATED)
        raise Http_error(409,Message.ALREADY_EXISTS)

    elif content.celery_task_id is not None:
        task_status = check_status(content.celery_task_id)
        status=task_status.get('inquiry_result')
        if status=='SUCCESS':
            content.content_generated = True
            logger.error(LogMsg.CONTENT_ALREADY_GENERATED)
            db_session.commit()

            raise Http_error(409,Message.ALREADY_EXISTS)
        elif status=='PENDING':
            logger.error(LogMsg.CONTENT_GENERATING)
            raise Http_error(409, Message.IN_PROCESS)

    content_data = return_content_full_path(content.content)
    content_data.update({'content_id':content_id})

    result = generate_book_content.apply_async(args=[content_data],
                                  routing_key='book_generate')
    content.celery_task_id=result.task_id
    print(result.task_id)
    # result.get()
    return {'inquiry_id':result.task_id}

def check_status(id):
    result = AsyncResult(id)
    return {'inquiry_result':result.status}



import os

from celery_works.celery_consumers import generate_book_content
from celery.result import AsyncResult

from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission, validate_permissions_and_access
from enums import Permissions
from helper import Http_error, value
from books.controllers.book_content import get_internal as get_content
from books.controllers.content_path_finder import return_content_full_path
from infrastructure.schema_validator import schema_validate
from log import logger, LogMsg
from messages import Message
from repository.book_repo import get as get_book
from .constants import GENERATE_BOOK_SCHEMA_PATH

book_saving_path = value('book_saving_path', '/home/nsm/book_sources')
if book_saving_path is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT, {'save_path': None})
    raise Http_error(500, Message.APP_CONFIG_MISSING)


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
            book.size = content_size(content_id)
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

def content_size(id):
    content_file_path = '{}/{}.msd'.format(book_saving_path, id)
    if not os.path.exists(content_file_path):
        return {'size':None}
    return {'size': os.path.getsize(content_file_path)}




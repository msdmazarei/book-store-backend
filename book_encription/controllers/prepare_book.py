import shutil

from book_library.controller import is_book_in_library
from books.controllers.book_content import get_be_data
from check_permission import get_user_permissions, has_permission
from enums import Permissions
from helper import Http_error, value
from log import LogMsg, logger
from messages import Message
from repository.content_repo import get_book_contents
from repository.library_repo import get as get_library
import os

from repository.user_repo import check_user

book_saving_path = value('book_saving_path', '/home/nsm/book_sources')
if book_saving_path is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT, {'save_path': None})
    raise Http_error(500, Message.APP_CONFIG_MISSING)

save_path = value('save_path', None)
if save_path is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT, {'save_path': None})
    raise Http_error(500, Message.APP_CONFIG_MISSING)


def prepare_book(book_id, db_session, username):
    logger.info(LogMsg.START, username)
    result = {}

    user = check_user(username, db_session)
    logger.error(LogMsg.LIBRARY_CHECK_BOOK_EXISTANCE,
                 {'person_id': user.person_id, 'book_id': book_id})


    brief_content = get_be_data(book_id, 'Brief', db_session)
    if brief_content is None:
        logger.error(LogMsg.NOT_FOUND, {'brief_content_of_book': book_id})
        raise Http_error(404, Message.NOT_FOUND)
    brief_path = copy_book_content_for_user(brief_content.id)
    result['Brief'] = brief_content.id
    logger.debug(LogMsg.PREPARE_BRIEF_ADDED, brief_path)

    if is_book_in_library(user.person_id, book_id, db_session):
        logger.debug(LogMsg.PREPARE_FULL_CONTENT,
                     {'person_id': user.person_id, 'book_id': book_id})


        per_data = {Permissions.IS_OWNER.value: True}
        permissions, presses = get_user_permissions(username, db_session)
        has_permission([Permissions.PREPARE_BOOK_PREMIUM],
                       permissions, None, per_data)

        logger.debug(LogMsg.PERMISSION_VERIFIED)

        content = get_be_data(book_id, 'Original', db_session)
        if content is None:
            logger.error(LogMsg.NOT_FOUND, {'original_content_of_book': book_id})
            raise Http_error(404, Message.NOT_FOUND)
        full_path = copy_book_content_for_user(content.id)

        logger.debug(LogMsg.PREPARE_ORIGINAL_ADDED,full_path)

        result['Original'] = content.id

    logger.info(LogMsg.END)
    return result


def copy_book_content_for_user(content_id):
    content_file_path = '{}/{}.msd'.format(book_saving_path, content_id)
    final_path = '{}/{}.msd'.format(save_path, content_id)
    shutil.copy(content_file_path, final_path, follow_symlinks=True)
    # os.rename(content_file_path,final_path)
    # os.close()
    return final_path

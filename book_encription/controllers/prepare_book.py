import shutil

from book_encription.controllers.device_key import user_device_exist
from book_library.controller import is_book_in_library
from books.controllers.book_content import get_be_data
from check_permission import get_user_permissions, has_permission
from enums import Permissions
from helper import Http_error, value, check_schema
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


def prepare_book(data, db_session, username):
    logger.info(LogMsg.START, username)
    result = {}
    check_schema(['book_id', 'device_id'], data.keys())
    book_id = data.get('book_id')
    device_id = data.get('device_id')

    user = check_user(username, db_session)
    logger.error(LogMsg.LIBRARY_CHECK_BOOK_EXISTANCE,
                 {'person_id': user.person_id, 'book_id': book_id})

    if not user_device_exist(user.id, device_id, db_session):
        logger.error(LogMsg.NOT_FOUND,
                     {'username': username, 'device_id': device_id})
        raise Http_error(404, Message.NOT_FOUND)

    brief_content = get_be_data(book_id, 'Brief', db_session)
    if brief_content is not None:
        if not is_generated(brief_content.id):
            logger.error(LogMsg.CONTENT_NOT_GENERATED,{'content_id':brief_content.id})
            raise Http_error(404,Message.BOOK_NOT_GENERATED)

        if is_prepared(brief_content,user.id):
            logger.debug(LogMsg.ALREADY_PREPARED,{'brief_content':brief_content.id})
            result['Brief'] ='{}_{}_{}'.format(user.id,brief_content.id,brief_content.version)
        else:
            brief_path = copy_book_content_for_user(brief_content,user.id)
            result['Brief'] = brief_path
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
            logger.error(LogMsg.NOT_FOUND,
                         {'original_content_of_book': book_id})
            return result

        if not is_generated(content.id):
            logger.error(LogMsg.CONTENT_NOT_GENERATED,{'content_id':content.id})
            raise Http_error(404,Message.BOOK_NOT_GENERATED)

        if is_prepared(content,user.id):
            logger.debug(LogMsg.ALREADY_PREPARED,{'original_content':content.id})
            result['Original'] ='{}_{}_{}'.format(user.id,content.id,content.version)
        else:

            full_path = copy_book_content_for_user(content,user.id)

            logger.debug(LogMsg.PREPARE_ORIGINAL_ADDED, full_path)

            result['Original'] = full_path

    logger.info(LogMsg.END)
    return result


def copy_book_content_for_user(content,user_id):
    content_file_path = '{}/{}.msd'.format(book_saving_path, content.id)
    file_name = '{}_{}_{}'.format(user_id,content.id,content.version)
    final_path = '{}/{}.msd'.format(save_path, file_name)
    shutil.copy(content_file_path, final_path, follow_symlinks=True)
    # os.rename(content_file_path,final_path)
    # os.close()
    return file_name


def is_prepared(content,user_id):

    file_name = '{}_{}_{}'.format(user_id, content.id,content.version)
    final_path = '{}/{}.msd'.format(save_path, file_name)
    logger.debug(LogMsg.CHECK_FILE_EXISTANCE, final_path)
    return os.path.exists(final_path)


def is_generated(content_id):
    content_file_path = '{}/{}.msd'.format(book_saving_path, content_id)
    return os.path.exists(content_file_path)


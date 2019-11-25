import shutil

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
    logger.error(LogMsg.APP_CONFIG_INCORRECT,{'save_path':None})
    raise Http_error(500,Message.APP_CONFIG_MISSING)

save_path = value('save_path',None)
if save_path is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT,{'save_path':None})
    raise Http_error(500,Message.APP_CONFIG_MISSING)

def prepare_book(library_id,db_session,username):
    logger.info(LogMsg.START,username)

    user = check_user(username,db_session)

    library_model = get_library(library_id,db_session)
    if library_model is None:
        logger.error(LogMsg.NOT_FOUND,{'library_id':library_id})
        raise Http_error(404,Message.NOT_FOUND)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if library_model.person_id == user.person_id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.PREPARE_BOOK_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED)

    book_id = library_model.book_id

    contents = get_book_contents(book_id, db_session)
    if contents is None:
        logger.error(LogMsg.NOT_FOUND,{'content_of_book':book_id})
        raise Http_error(404,Message.NOT_FOUND)
    res = []
    for content in contents:
        content_file_path = '{}/{}.msd'.format(book_saving_path, content.id)
        final_path = '{}/{}.msd'.format(save_path, content.id)
        shutil.copy(content_file_path, final_path, follow_symlinks=True)
        # os.rename(content_file_path,final_path)
        # os.close()
        res.append(final_path)
    logger.info(LogMsg.END)
    return res


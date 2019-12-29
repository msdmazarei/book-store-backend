import os
from uuid import uuid4

import magic
from bottle import response, static_file

from helper import value, Http_error, Http_response
from infrastructure.schema_validator import schema_validate
from log import logger, LogMsg
from messages import Message
from .constants import UPLOAD_SCHEMA_PATH,DELETE_SCHEMA_PATH

save_path = value('save_path',None)


def upload_files(data, **kwargs):
    schema_validate(data,UPLOAD_SCHEMA_PATH)
    try:
        files_list = data.get('files')
        model_files  =[]
        if files_list and len(files_list) > 0:
            for file in files_list:
                if file:
                    file.filename = str(uuid4())
                    model_files.append(file.filename)

                    file.save(save_path)

        return model_files
    except:
        logger.exception(LogMsg.UPLOAD_FAILED,exc_info=True)
        raise Http_error(405,Message.UPLOAD_FAILED)



def delete_files(files, **kwargs):
    try:
        for filename in files:
            file_path = '{}/{}'.format(save_path,filename)
            logger.debug('file_path is %s ',file_path)

            if os.path.isfile(file_path):
                logger.debug(LogMsg.FILE_EXISTS,file_path)
                os.remove(file_path)
            else:
                logger.debug(LogMsg.FILE_NOT_EXISTS,file_path)
    except:
        logger.exception(LogMsg.DELETE_FAILED,exc_info=True)
        raise Http_error(404,Message.NOT_FOUND)
    logger.debug(LogMsg.DELETE_SUCCESS)
    return True



def return_file(filename, **kwargs):
    try:

        response.body = static_file(filename, root=save_path)
        file_path = '{}/{}'.format(save_path,filename)
        if os.path.isfile(file_path):
            logger.debug(LogMsg.FILE_EXISTS, file_path)
            response.content_type = file_mime_type(file_path)
        else:
            logger.debug(LogMsg.FILE_NOT_EXISTS, file_path)
        return response
    except:
        logger.exception(LogMsg.FILE_NOT_EXISTS,exc_info=True)
        raise Http_error(404,Message.NOT_FOUND)



def file_mime_type(file_path):
    m = magic.from_file(file_path, mime=True)
    return str(m)


def delete_multiple_files(data,**kwargs):
    schema_validate(data,DELETE_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)
    files  = data.get('files')
    delete_files(files)
    return Http_response(204,True)
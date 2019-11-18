from helper import value, Http_error
from log import logger, LogMsg
from messages import Message

main_path = value('save_path',None)
if main_path is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT,{'save_path':None})


def return_content_full_path(content):
    logger.info(LogMsg.START,'')

    if content.get('body',None) is not None:
        # body is a list of json objects
        replace_full_path(content.get('body'))
    if content.get('children',None) is not  None:
        children = content.get('children')
        for child in children:
            return_content_full_path(child)
    return content



def replace_full_path(file_list):
    for item in file_list:
        key = item.get('type',None)
        if key is None:
            logger.error(LogMsg.DATA_MISSING,{'body.type':None})
            raise Http_error(404,Message.MISSING_REQUIERED_FIELD)
        file_name = item.get(key)
        if file_name is None:
            logger.error(LogMsg.DATA_MISSING, {'body.file': None})
            raise Http_error(404, Message.MISSING_REQUIERED_FIELD)
        full_path = '{}/{}'.format(main_path,file_name)
        item[key] = full_path
    return True



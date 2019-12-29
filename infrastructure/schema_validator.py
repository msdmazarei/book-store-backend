import jsonschema
import json

from helper import Http_error
from log import logger, LogMsg
from messages import Message


def schema_validate(data,schema_file):
    try:

        with open(schema_file, 'r') as f:
            schema_data = f.read()
        schema = json.loads(schema_data)

        jsonschema.validate(data, schema)
        logger.debug(LogMsg.SCHEMA_CHECKED)
    except:
        logger.exception(LogMsg.SCHEMA_NOT_VALID,exc_info=True)
        raise Http_error(405,Message.SCHEMA_NOT_VALID)
    return True
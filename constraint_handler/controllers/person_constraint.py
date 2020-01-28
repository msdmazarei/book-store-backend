from constraint_handler.models import ConstraintHandler
from log import logger, LogMsg
from helper import populate_basic_data, Http_error, Http_response
from messages import Message

def add(model, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, model)

    try:
        unique_code = ConstraintHandler()
        populate_basic_data(unique_code, 'INTERNAL', None)

        the_code = persons_code(model)
        unique_code.UniqueCode = the_code

        logger.debug(LogMsg.UNIQUE_CONSTRAINT_IS, the_code)

        db_session.add(unique_code)
        db_session.flush()
    except:
        logger.exception(LogMsg.UNIQUE_CONSTRAINT_EXISTS,exc_info=True)
        raise Http_error(409,Message.ALREADY_EXISTS)

    logger.info(LogMsg.END)

    return unique_code


def persons_code(model):

    return 'PERSON-{}-{}-{}'.format(model.name, model.last_name, model.cell_no)
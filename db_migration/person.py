from log import logger, LogMsg
from repository.user_repo import check_user
from user.models import Person


def full_name_settling(db_session,username):
    logger.info(LogMsg.START,username)
    persons = db_session.query(Person).filter(Person.full_name==None).all()

    for person in persons:
        if person.last_name is None:
            person.full_name = person.name
        elif person.name is None:
            person.full_name = person.last_name
        else:
            person.full_name = '{} {}'.format(person.name or '',person.last_name or '')
    return {'result':True}
from log import logger, LogMsg
from repository.user_repo import check_user
from user.models import Person


def full_name_settling(db_session,username):
    logger.info(LogMsg.START,username)
    persons = db_session.query(Person).filter(Person.full_name==None).all()
    res = list()
    for person in persons:
        if person.last_name is None or '':
            person.full_name = person.name
        elif person.name is None or '':
            person.full_name = person.last_name
        else:
            person.full_name = '{} {}'.format(person.last_name ,person.name)
        res.append(person.full_name)
    return {'result':res}




def full_name_erasing(db_session,username):
    logger.info(LogMsg.START,username)
    persons = db_session.query(Person).all()
    for person in persons:
        person.full_name = None
    return {'result':True}
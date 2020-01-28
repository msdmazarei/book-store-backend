import datetime
from uuid import uuid4

from user.models import Person,User
from group.models import Group,GroupUser


def init_db(db_session):
    person = Person()
    person.id = str(uuid4())
    person.version =1
    person.creation_date = datetime.datetime.now()
    person.creator = 'DB_INIT'
    person.name = 'Admin'
    person.last_name = 'Admin'
    person.cell_no = '11111111111'
    db_session.add(person)

    return {'result':'successful'}
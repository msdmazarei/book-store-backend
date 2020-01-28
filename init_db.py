import datetime
from uuid import uuid4

from db_migration.permissions import permissions_to_db
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

    user = User()
    user.id = str(uuid4())
    user.version = 1
    user.creation_date = datetime.datetime.now()
    user.creator = 'DB_INIT'
    user.username = 'Admin'
    user.password = 'Admin'
    user.person_id = person.id

    db_session.add(user)

    group = Group()
    group.id = str(uuid4())
    group.version = 1
    group.creation_date = datetime.datetime.now()
    group.creator = 'DB_INIT'
    group.title = 'Administrators'
    group.person_id = person.id

    db_session.add(group)

    gu = GroupUser()
    gu.id = str(uuid4())
    gu.version = 1
    gu.creation_date = datetime.datetime.now()
    gu.creator = 'DB_INIT'
    gu.group_id = group.id
    gu.user_id = user.id

    db_session.add(gu)

    permissions_to_db(db_session, user.username)


    return {'result':'successful'}
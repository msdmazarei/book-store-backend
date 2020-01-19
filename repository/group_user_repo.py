from uuid import uuid4

from group.models import GroupUser
from helper import Now
from repository.group_repo import validate_groups


def delete_group_users(group_id, db_session):
    db_session.query(GroupUser).filter(GroupUser.group_id == group_id).delete()
    return True


def delete_user_from_groups(user_id, db_session):
    db_session.query(GroupUser).filter(GroupUser.user_id == user_id).delete()
    return True


def get_user_group_list(user_id, db_session):
    result = db_session.query(GroupUser).filter(
        GroupUser.user_id == user_id).all()

    groups = []
    for item in result:
        groups.append(item.group_id)
    group_persons_list = validate_groups(groups, db_session)
    group_persons = {}
    for item in group_persons_list:
        group_persons.update({item.id: item.person_id})
    return group_persons


def users_of_groups(group_list, db_session):
    group_users = db_session.query(GroupUser).filter(
        GroupUser.group_id.in_(group_list)).all()

    users = []
    for item in group_users:
        users.append(item.user_id)

    result = set(users)
    return result


def user_is_in_group(user_id, group_id, db_session):
    result = db_session.query(GroupUser).filter(GroupUser.user_id == user_id,
                                                GroupUser.group_id == group_id).first()
    if result is None:
        return False
    return True


def add_owner_to_group_users(group_id, user_id, db_session, username):
    model_instance = GroupUser()
    model_instance.id = uuid4()
    model_instance.group_id = group_id
    model_instance.user_id = user_id
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    db_session.add(model_instance)
    return model_instance


def user_is_in_group_list(user_id, group_list, db_session):
    result = db_session.query(GroupUser).filter(GroupUser.user_id == user_id,
                                                GroupUser.group_id.in_(group_list)).all()
    final_res = []
    for item in result:
        final_res.append(item.group_id)

    return final_res
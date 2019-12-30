from permission.models import GroupPermission


def get_permission_list_of_groups(group_list, db_session):
    groups = set(group_list)
    result = db_session.query(GroupPermission).filter(
        GroupPermission.group_id.in_(groups)).all()

    permissions = []
    for item in result:
        permissions.append(str(item.permission_id))
    return set(permissions)

def delete_all_permissions_of_group(group_id, db_session):
    db_session.query(GroupPermission).filter(
        GroupPermission.group_id == group_id).delete()
    return True
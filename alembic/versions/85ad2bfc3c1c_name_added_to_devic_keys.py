"""name added to devic_keys

Revision ID: 85ad2bfc3c1c
Revises: b0477ed025d9
Create Date: 2019-12-04 13:59:51.689928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85ad2bfc3c1c'
down_revision = 'b0477ed025d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('book_contents_id_key', 'book_contents', type_='unique')
    op.create_unique_constraint(op.f('book_contents_id_key'), 'book_contents', ['id'])
    op.add_column('device_codes', sa.Column('name', sa.String(), nullable=True))
    op.drop_constraint('device_codes_id_key', 'device_codes', type_='unique')
    op.create_unique_constraint(op.f('device_codes_id_key'), 'device_codes', ['id'])
    op.drop_constraint('discussion_members_id_key', 'discussion_members', type_='unique')
    op.create_unique_constraint(op.f('discussion_members_id_key'), 'discussion_members', ['group_id', 'person_id'])
    op.drop_constraint('group_permissions_id_key', 'group_permissions', type_='unique')
    op.create_unique_constraint(op.f('group_permissions_id_key'), 'group_permissions', ['group_id', 'permission_id'])
    op.drop_constraint('groups_id_key', 'groups', type_='unique')
    op.create_unique_constraint(op.f('groups_id_key'), 'groups', ['id'])
    op.drop_constraint('permissions_id_key', 'permissions', type_='unique')
    op.create_unique_constraint(op.f('permissions_id_key'), 'permissions', ['permission'])
    op.drop_constraint('persons_id_key', 'persons', type_='unique')
    op.create_unique_constraint(op.f('persons_id_key'), 'persons', ['id'])
    op.drop_constraint('unique_entity_connector_id_key', 'unique_entity_connector', type_='unique')
    op.create_unique_constraint(op.f('unique_entity_connector_id_key'), 'unique_entity_connector', ['UniqueCode', 'entity_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('unique_entity_connector_id_key'), 'unique_entity_connector', type_='unique')
    op.create_unique_constraint('unique_entity_connector_id_key', 'unique_entity_connector', ['id'])
    op.drop_constraint(op.f('persons_id_key'), 'persons', type_='unique')
    op.create_unique_constraint('persons_id_key', 'persons', ['email'])
    op.drop_constraint(op.f('permissions_id_key'), 'permissions', type_='unique')
    op.create_unique_constraint('permissions_id_key', 'permissions', ['id'])
    op.drop_constraint(op.f('groups_id_key'), 'groups', type_='unique')
    op.create_unique_constraint('groups_id_key', 'groups', ['title'])
    op.drop_constraint(op.f('group_permissions_id_key'), 'group_permissions', type_='unique')
    op.create_unique_constraint('group_permissions_id_key', 'group_permissions', ['id'])
    op.drop_constraint(op.f('discussion_members_id_key'), 'discussion_members', type_='unique')
    op.create_unique_constraint('discussion_members_id_key', 'discussion_members', ['id'])
    op.drop_constraint(op.f('device_codes_id_key'), 'device_codes', type_='unique')
    op.create_unique_constraint('device_codes_id_key', 'device_codes', ['code'])
    op.drop_column('device_codes', 'name')
    op.drop_constraint(op.f('book_contents_id_key'), 'book_contents', type_='unique')
    op.create_unique_constraint('book_contents_id_key', 'book_contents', ['book_id', 'type'])
    # ### end Alembic commands ###
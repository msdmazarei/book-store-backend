"""group--person_id added

Revision ID: 54f888931815
Revises: 9526a68e6e06
Create Date: 2019-10-09 13:06:16.355314

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '54f888931815'
down_revision = '9526a68e6e06'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'group_permissions', ['id'])
    op.add_column('groups', sa.Column('person_id', postgresql.UUID(), nullable=True))
    op.create_foreign_key(None, 'groups', 'persons', ['person_id'], ['id'])
    op.create_unique_constraint(None, 'permissions', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'permissions', type_='unique')
    op.drop_constraint(None, 'groups', type_='foreignkey')
    op.drop_column('groups', 'person_id')
    op.drop_constraint(None, 'group_permissions', type_='unique')
    # ### end Alembic commands ###
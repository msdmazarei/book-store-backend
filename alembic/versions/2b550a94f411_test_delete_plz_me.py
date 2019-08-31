"""test--delete plz me

Revision ID: 2b550a94f411
Revises: 112939a9c20a
Create Date: 2019-08-31 23:19:12.751328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b550a94f411'
down_revision = '112939a9c20a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'unique_entity_connector', ['UniqueCode'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'unique_entity_connector', type_='unique')
    # ### end Alembic commands ###
"""test--delete plz me

Revision ID: f542f13d6882
Revises: 2b550a94f411
Create Date: 2019-08-31 23:22:06.839228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f542f13d6882'
down_revision = '2b550a94f411'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_entity_connector_UniqueCode_key', 'unique_entity_connector', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_entity_connector_UniqueCode_key', 'unique_entity_connector', ['UniqueCode'])
    # ### end Alembic commands ###
"""some unique added

Revision ID: 112939a9c20a
Revises: 7416539768d7
Create Date: 2019-08-28 11:39:23.036972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '112939a9c20a'
down_revision = '7416539768d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'prices', ['book_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'prices', type_='unique')
    # ### end Alembic commands ###

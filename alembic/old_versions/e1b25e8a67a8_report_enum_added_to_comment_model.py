"""report enum added to comment model

Revision ID: e1b25e8a67a8
Revises: d7cfe1b05984
Create Date: 2019-07-17 13:02:36.758489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.dialects import postgresql

revision = 'e1b25e8a67a8'
down_revision = 'd7cfe1b05984'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    reportcomment = postgresql.ENUM('Personal', 'Invalid_Content', name='reportcomment')
    reportcomment.create(op.get_bind())

    op.add_column('comments', sa.Column('report', sa.Enum('Personal', 'Invalid_Content', name='reportcomment'), nullable=True))
    op.create_unique_constraint(None, 'comments', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_constraint(None, 'comments', type_='unique')
    op.drop_column('comments', 'report')
    # ### end Alembic commands ###

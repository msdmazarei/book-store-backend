"""comment

Revision ID: a7d2d41f6f29
Revises: 2a8dd0d5afc1
Create Date: 2019-06-03 10:03:58.177887

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a7d2d41f6f29'
down_revision = '2a8dd0d5afc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('image', postgresql.UUID(), nullable=True))
    op.add_column('users', sa.Column('library', postgresql.ARRAY(sa.String()), nullable=True))
    op.drop_column('users', 'basket')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('basket', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_column('users', 'library')
    op.drop_column('users', 'image')
    # ### end Alembic commands ###

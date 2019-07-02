"""genre in book changed

Revision ID: 5484dee1e0f7
Revises: 3035567744cb
Create Date: 2019-07-01 15:27:20.285898

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5484dee1e0f7'
down_revision = '3035567744cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('genre', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'genre')
    # ### end Alembic commands ###

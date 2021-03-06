"""files added to book model

Revision ID: 4194b9ee7aa1
Revises: 5484dee1e0f7
Create Date: 2019-07-03 13:37:28.077280

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4194b9ee7aa1'
down_revision = '5484dee1e0f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('files', postgresql.ARRAY(postgresql.UUID()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'files')
    # ### end Alembic commands ###

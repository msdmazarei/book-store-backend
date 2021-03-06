"""is_legal added to person

Revision ID: f242443e38c7
Revises: 602265aff076
Create Date: 2019-10-12 17:30:49.221419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f242443e38c7'
down_revision = '602265aff076'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('persons', sa.Column('is_legal', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('persons', 'is_legal')
    # ### end Alembic commands ###

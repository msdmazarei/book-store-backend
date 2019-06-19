"""user controller and token added to project

Revision ID: ac5a6b8b7bc4
Revises: eec76ea91ddd
Create Date: 2019-06-03 12:19:32.649596

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ac5a6b8b7bc4'
down_revision = 'eec76ea91ddd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_tokens',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('expiration_date', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('app_tokens')
    # ### end Alembic commands ###
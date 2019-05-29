"""tag added to primary model

Revision ID: 5dc6b49b1ab2
Revises: fb6e23153b05
Create Date: 2019-05-28 10:35:23.224445

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5dc6b49b1ab2'
down_revision = 'fb6e23153b05'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('addresses', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('users', sa.Column('basket', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('users', sa.Column('phones', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('users', sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'tags')
    op.drop_column('users', 'phones')
    op.drop_column('users', 'basket')
    op.drop_column('users', 'addresses')
    # ### end Alembic commands ###

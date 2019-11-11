"""payment table added

Revision ID: 585ba4a0bf50
Revises: 3790bfefc97f
Create Date: 2019-11-06 14:18:28.296649

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '585ba4a0bf50'
down_revision = '3790bfefc97f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payments',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('person_id', postgresql.UUID(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('shopping_key', sa.String(), nullable=True),
    sa.Column('reference_code', sa.String(), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('order_details', sa.JSON(), nullable=True),
    sa.Column('agent', sa.String(), nullable=True),
    sa.Column('used', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_unique_constraint(None, 'last_seens', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'last_seens', type_='unique')
    op.drop_table('payments')
    # ### end Alembic commands ###
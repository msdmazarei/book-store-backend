"""unique_entitiy_connector added

Revision ID: 337fd52a66a8
Revises: 690ec24ff365
Create Date: 2019-08-27 14:18:44.861613

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '337fd52a66a8'
down_revision = '690ec24ff365'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('unique_entity_connector',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('UniqueCode', sa.String(), nullable=False),
    sa.Column('entity_id', postgresql.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('UniqueCode'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('unique_entity_connector')
    # ### end Alembic commands ###

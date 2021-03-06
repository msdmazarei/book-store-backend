"""messaging model added

Revision ID: 4c459ce0c059
Revises: 2cded5384f4a
Create Date: 2019-10-21 15:06:02.707865

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4c459ce0c059'
down_revision = '2cded5384f4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_messages',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('sender_id', postgresql.UUID(), nullable=False),
    sa.Column('receptor_id', postgresql.UUID(), nullable=True),
    sa.Column('group_id', postgresql.UUID(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('parent_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['discussion_groups.id'], ),
    sa.ForeignKeyConstraint(['receptor_id'], ['persons.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_unique_constraint(None, 'discussion_groups', ['id'])
    op.create_unique_constraint(None, 'discussion_members', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'discussion_members', type_='unique')
    op.drop_constraint(None, 'discussion_groups', type_='unique')
    op.drop_table('chat_messages')
    # ### end Alembic commands ###

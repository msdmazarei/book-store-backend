"""comment entity added to prj

Revision ID: d7cfe1b05984
Revises: 3a55433ca46a
Create Date: 2019-07-17 12:05:00.053993

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd7cfe1b05984'
down_revision = '3a55433ca46a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('book_id', postgresql.UUID(), nullable=False),
    sa.Column('person_id', postgresql.UUID(), nullable=False),
    sa.Column('parent_id', postgresql.UUID(), nullable=True),
    sa.Column('helpful', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.drop_column('persons', 'following_list')
    op.drop_column('persons', 'follower_list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('persons', sa.Column('follower_list', postgresql.ARRAY(postgresql.UUID()), autoincrement=False, nullable=True))
    op.add_column('persons', sa.Column('following_list', postgresql.ARRAY(postgresql.UUID()), autoincrement=False, nullable=True))
    op.drop_table('comments')
    # ### end Alembic commands ###

"""Book content table added

Revision ID: 4e17ab85b61d
Revises: e43690dc1811
Create Date: 2019-11-10 12:45:15.127063

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4e17ab85b61d'
down_revision = 'e43690dc1811'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book_contents',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('book_id', postgresql.UUID(), nullable=False),
    sa.Column('type', sa.Enum('Brief', 'Original', name='bookcontenttype'), nullable=False),
    sa.Column('content', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], name=op.f('fk_tb_book_contents_col_book_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_book_contents')),
    sa.UniqueConstraint('id', name=op.f('book_contents_id_key'))
    )
    op.drop_constraint('constraints_id_key', 'constraints', type_='unique')
    op.create_unique_constraint(op.f('constraints_id_key'), 'constraints', ['UniqueCode'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('constraints_id_key'), 'constraints', type_='unique')
    op.create_unique_constraint('constraints_id_key', 'constraints', ['id'])
    op.drop_table('book_contents')
    # ### end Alembic commands ###

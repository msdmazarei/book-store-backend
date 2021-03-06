"""adding booktype ,library and book-role to book module

Revision ID: 4473e6dd7e1d
Revises: 9b50737deed8
Create Date: 2019-06-16 10:21:04.182856

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4473e6dd7e1d'
down_revision = '9b50737deed8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('edition', sa.String(), nullable=True),
    sa.Column('pub_year', sa.Integer(), nullable=True),
    sa.Column('type', sa.Enum('DVD', 'Audio', 'Hard_Copy', 'Pdf', 'Epub', name='booktypes'), nullable=True),
    sa.Column('genre', sa.Enum('Comedy', 'Drama', 'Romance', 'Social', 'Religious', 'Historical', name='genre'), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('rate', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book_roles',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('book_id', postgresql.UUID(), nullable=False),
    sa.Column('preson_id', postgresql.UUID(), nullable=False),
    sa.Column('role', sa.Enum('Author', 'Writer', 'Translator', 'Press', 'Contributer', 'Designer', name='roles'), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['preson_id'], ['presons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('book_roles')
    op.drop_table('books')
    # ### end Alembic commands ###

"""constraints on person added to user and bookrole

Revision ID: 806ef17af6eb
Revises: 4276a6e90754
Create Date: 2019-06-17 14:11:49.061907

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '806ef17af6eb'
down_revision = '4276a6e90754'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('book_roles', sa.Column('person_id', postgresql.UUID(), nullable=False))
    op.create_foreign_key(None, 'book_roles', 'persons', ['person_id'], ['id'])
    op.create_unique_constraint(None, 'persons', ['id'])
    op.add_column('users', sa.Column('person_id', postgresql.UUID(), nullable=True))
    op.create_foreign_key(None, 'users', 'persons', ['person_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'person_id')
    op.drop_constraint(None, 'persons', type_='unique')
    op.drop_constraint(None, 'book_roles', type_='foreignkey')
    op.drop_column('book_roles', 'person_id')
    # ### end Alembic commands ###

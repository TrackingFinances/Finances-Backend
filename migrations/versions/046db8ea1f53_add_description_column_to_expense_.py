"""Add description column to expense,investment,income tables

Revision ID: 046db8ea1f53
Revises: 991e86e02732
Create Date: 2024-09-09 22:04:14.692434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '046db8ea1f53'
down_revision = '991e86e02732'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))

    with op.batch_alter_table('incomes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))

    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('incomes', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###

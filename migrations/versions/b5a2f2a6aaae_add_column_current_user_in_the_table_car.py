"""Add column current_user in the table Car

Revision ID: b5a2f2a6aaae
Revises: 5ff715192b1a
Create Date: 2021-02-10 14:42:30.211560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5a2f2a6aaae'
down_revision = '5ff715192b1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('car', sa.Column('current_user', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('car', 'current_user')
    # ### end Alembic commands ###

"""Add Table Rental_log and relationship

Revision ID: b177b68f3b83
Revises: b5a2f2a6aaae
Create Date: 2021-02-10 17:09:46.384535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b177b68f3b83'
down_revision = 'b5a2f2a6aaae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rental_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('car_id', sa.Integer(), nullable=True),
    sa.Column('start_rental_time', sa.DateTime(), nullable=True),
    sa.Column('end_rental_time', sa.DateTime(), nullable=True),
    sa.Column('cost_rental', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rental_log')
    # ### end Alembic commands ###

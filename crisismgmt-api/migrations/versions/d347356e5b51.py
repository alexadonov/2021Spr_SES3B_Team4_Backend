"""empty message

Revision ID: d347356e5b51
Revises: c4b6629eee26
Create Date: 2021-09-13 12:48:41.719215

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
revision = 'd347356e5b51'
down_revision = 'c4b6629eee26'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('request_list', 
    sa.Column('request_list_id', (sa.Integer()), autoincrement=True, nullable=False), 
    sa.Column('user_id', (sa.Integer()), nullable=True), 
    sa.Column('request_user_id', (sa.Integer()), nullable=True), 
    sa.Column('content', sa.String(length=255), nullable=False), 
    sa.Column('status', sa.String(length=191), nullable=False), 
    sa.Column('reason', sa.String(length=255), nullable=True), 
    sa.ForeignKeyConstraint(['request_user_id'], ['users.user_id'], ondelete='CASCADE'), 
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'), 
    sa.PrimaryKeyConstraint('request_list_id')
    )
    op.drop_column('event', 'radius')


def downgrade():
    op.add_column('event', sa.Column('radius', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_table('request_list')
"""empty message

Revision ID: 03a23fe79ff7
Revises: 
Create Date: 2024-11-27 09:49:01.942503

"""
from alembic import op
import sqlalchemy as sa
import notes.domain.sql


# revision identifiers, used by Alembic.
revision = '03a23fe79ff7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note_user',
    sa.Column('id', sa.String(length=511), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('notes',
    sa.Column('note_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('owner_id', sa.String(length=511), nullable=False),
    sa.Column('note_description', sa.String(length=512), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['note_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('note_id')
    )
    op.create_table('note_share',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.String(length=511), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['notes.note_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['note_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('note_share')
    op.drop_table('notes')
    op.drop_table('note_user')
    # ### end Alembic commands ###

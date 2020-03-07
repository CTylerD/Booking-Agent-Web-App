"""empty message

Revision ID: 629e46fb0928
Revises: 9b477df536e5
Create Date: 2020-03-06 14:29:41.882551

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '629e46fb0928'
down_revision = '9b477df536e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'genres',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               type_=sa.ARRAY(sa.String()),
               existing_nullable=True)
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               type_=sa.String(),
               existing_nullable=True)
    op.drop_column('artists', 'upcoming_shows_count')
    op.drop_column('artists', 'past_shows_count')
    op.drop_column('artists', 'show_lists')
    op.alter_column('shows', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('venues', 'genres',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               type_=sa.ARRAY(sa.String()),
               existing_nullable=True)
    op.alter_column('venues', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               type_=sa.String(),
               existing_nullable=True)
    op.drop_column('venues', 'upcoming_shows')
    op.drop_column('venues', 'past_shows_count')
    op.drop_column('venues', 'past_shows')
    op.drop_column('venues', 'upcoming_shows_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('venues', sa.Column('past_shows', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('venues', sa.Column('past_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('venues', sa.Column('upcoming_shows', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.alter_column('venues', 'seeking_talent',
               existing_type=sa.String(),
               type_=sa.BOOLEAN(),
               existing_nullable=True)
    op.alter_column('venues', 'genres',
               existing_type=sa.ARRAY(sa.String()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=True)
    op.alter_column('shows', 'start_time',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.add_column('artists', sa.Column('show_lists', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('artists', sa.Column('past_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('artists', sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.String(),
               type_=sa.BOOLEAN(),
               existing_nullable=True)
    op.alter_column('artists', 'genres',
               existing_type=sa.ARRAY(sa.String()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=True)
    # ### end Alembic commands ###

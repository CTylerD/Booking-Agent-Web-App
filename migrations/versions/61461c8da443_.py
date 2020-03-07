"""empty message

Revision ID: 61461c8da443
Revises: 6dd2b97f8f02
Create Date: 2020-03-05 15:48:08.233241

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '61461c8da443'
down_revision = '6dd2b97f8f02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('past_shows', sa.JSON(), nullable=True))
    op.add_column('artists', sa.Column('upcoming_shows', sa.JSON(), nullable=True))
    op.drop_column('artists', 'show_lists')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('show_lists', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_column('artists', 'upcoming_shows')
    op.drop_column('artists', 'past_shows')
    # ### end Alembic commands ###

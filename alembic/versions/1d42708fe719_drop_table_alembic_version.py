"""DROP TABLE alembic_version

Revision ID: 1d42708fe719
Revises: a029e7d481be
Create Date: 2018-01-25 04:50:57.147522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d42708fe719'
down_revision = 'a029e7d481be'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

"""video.created_by to text

Revision ID: 5c4f8719e692
Revises: 0f56d02d723e
Create Date: 2025-09-18 09:56:48.255733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5c4f8719e692'
down_revision: Union[str, None] = '0f56d02d723e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'video',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('preview_img', sa.String(), nullable=False),
        sa.Column('video', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='Active'),
        sa.Column('created_at', sa.DateTime(timezone=False), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=False), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=False), nullable=True),
    )



def downgrade() -> None:
    """Downgrade schema."""
    pass

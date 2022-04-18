"""create_rating_table

Revision ID: 1e33feaefa51
Revises: 2e2154fb2d88
Create Date: 2022-04-15 12:01:56.793127

"""
from alembic import op
from typing import Tuple
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e33feaefa51'
down_revision = '2e2154fb2d88'
branch_labels = None
depends_on = None


def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )


def create_rating_table() -> None:
    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("movie_id", sa.Integer, nullable=False, index=True),
        sa.Column(
            "user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("grade", sa.Integer, nullable=False),
        *timestamps()
    )
    op.execute(
        """
        ALTER TABLE ratings
        ADD UNIQUE (movie_id, user_id)
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_rating_modtime
            BEFORE UPDATE
            ON ratings
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    create_rating_table()


def downgrade() -> None:
    op.drop_table("ratings")

"""
A new table named token_blocklist has been added to store revoked tokens.

Revision ID: ad787fff640a
Revises: fbbd12061c83
Create Date: 2024-03-24 18:28:53.885626

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ad787fff640a"
down_revision = "fbbd12061c83"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "token_blocklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("token_blocklist")
    # ### end Alembic commands ###

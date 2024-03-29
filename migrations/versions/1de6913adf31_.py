"""empty message

Revision ID: 1de6913adf31
Revises: f396281fcae1
Create Date: 2024-03-09 22:38:24.101414

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1de6913adf31'
down_revision = 'f396281fcae1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('unit', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_type_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key("FK_data_data_type", 'data_type', ['data_type_id'], ['id'])
        batch_op.drop_column('data_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_type', postgresql.ENUM('TEMPERATURE', 'FUEL_LEVEL', 'EXCAVATED', name='datatypeenum'), autoincrement=False, nullable=True))
        batch_op.drop_constraint("FK_data_data_type", type_='foreignkey')
        batch_op.drop_column('data_type_id')

    op.drop_table('data_type')
    # ### end Alembic commands ###

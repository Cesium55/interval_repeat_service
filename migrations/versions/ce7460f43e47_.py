"""empty message

Revision ID: ce7460f43e47
Revises: 
Create Date: 2025-07-23 15:43:25.964754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce7460f43e47'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('learn_statuses',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('repeat_entities',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], ['repeat_entities.id'], ),
    sa.PrimaryKeyConstraint('id', 'entity_id')
    )
    op.create_table('repeat_entity_instances',
    sa.Column('entity_type', sa.Integer(), nullable=False),
    sa.Column('instance_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['entity_type'], ['repeat_entities.id'], ),
    sa.PrimaryKeyConstraint('entity_type', 'instance_id')
    )
    op.create_table('repeat_relations',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('entity_type', sa.Integer(), nullable=False),
    sa.Column('instance_id', sa.Integer(), nullable=False),
    sa.Column('current_iteration', sa.Integer(), nullable=True),
    sa.Column('last_repeated', sa.TIMESTAMP(), nullable=True),
    sa.Column('next_repeat_time', sa.TIMESTAMP(), nullable=True),
    sa.Column('forgot_times', sa.Integer(), nullable=True),
    sa.Column('learn_status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['entity_type'], ['repeat_entities.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'entity_type', 'instance_id')
    )
    op.create_table('group_instance_relations',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.Column('instance_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id', 'entity_id'], ['groups.id', 'groups.entity_id'], ),
    sa.PrimaryKeyConstraint('group_id', 'entity_id', 'instance_id')
    )
    op.create_table('user_group_relations',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id', 'entity_id'], ['groups.id', 'groups.entity_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'group_id', 'entity_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_group_relations')
    op.drop_table('group_instance_relations')
    op.drop_table('repeat_relations')
    op.drop_table('repeat_entity_instances')
    op.drop_table('groups')
    op.drop_table('repeat_entities')
    op.drop_table('learn_statuses')
    # ### end Alembic commands ###

"""tz_aware_travel_run_timestamps

Revision ID: d678d6de706f
Revises: 134b62b01968
Create Date: 2026-10-16 02:49:12.362749
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd678d6de706f'
down_revision: Union[str, None] = '134b62b01968'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. travel_runs: alter started_at and completed_at to TIMESTAMP WITH TIME ZONE
    with op.batch_alter_table('travel_runs') as batch_op:
        batch_op.alter_column(
            'started_at',
            type_=sa.DateTime(timezone=True),
            postgresql_using="started_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=False),
            existing_nullable=True,
        )
        batch_op.alter_column(
            'completed_at',
            type_=sa.DateTime(timezone=True),
            postgresql_using="completed_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=False),
            existing_nullable=True,
        )

    # 2. transport_options: alter retrieved_at to TIMESTAMP WITH TIME ZONE
    with op.batch_alter_table('transport_options') as batch_op:
        batch_op.alter_column(
            'retrieved_at',
            type_=sa.DateTime(timezone=True),
            postgresql_using="retrieved_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=False),
            existing_nullable=False,
        )

    # 3. accommodation_options: alter retrieved_at to TIMESTAMP WITH TIME ZONE
    with op.batch_alter_table('accommodation_options') as batch_op:
        batch_op.alter_column(
            'retrieved_at',
            type_=sa.DateTime(timezone=True),
            postgresql_using="retrieved_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=False),
            existing_nullable=False,
        )

    # 4. memory_entries: alter expires_at to TIMESTAMP WITH TIME ZONE
    with op.batch_alter_table('memory_entries') as batch_op:
        batch_op.alter_column(
            'expires_at',
            type_=sa.DateTime(timezone=True),
            postgresql_using="expires_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=False),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table('memory_entries') as batch_op:
        batch_op.alter_column(
            'expires_at',
            type_=sa.DateTime(timezone=False),
            postgresql_using="expires_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )

    with op.batch_alter_table('accommodation_options') as batch_op:
        batch_op.alter_column(
            'retrieved_at',
            type_=sa.DateTime(timezone=False),
            postgresql_using="retrieved_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table('transport_options') as batch_op:
        batch_op.alter_column(
            'retrieved_at',
            type_=sa.DateTime(timezone=False),
            postgresql_using="retrieved_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table('travel_runs') as batch_op:
        batch_op.alter_column(
            'completed_at',
            type_=sa.DateTime(timezone=False),
            postgresql_using="completed_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )
        batch_op.alter_column(
            'started_at',
            type_=sa.DateTime(timezone=False),
            postgresql_using="started_at AT TIME ZONE 'UTC'",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )

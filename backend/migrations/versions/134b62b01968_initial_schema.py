"""initial_schema

Revision ID: 134b62b01968
Revises: 
Create Date: 2026-10-15 18:18:13.836714
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '134b62b01968'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    try:
        inspector = sa.inspect(conn)
        existing_tables = set(inspector.get_table_names())
    except Exception:
        existing_tables = set()

    # --- 1. users ---
    if "users" not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('hashed_password', sa.String(), nullable=True),
            sa.Column('display_name', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    else:
        try:
            existing_cols = {c['name'] for c in inspector.get_columns('users')}
        except Exception:
            existing_cols = set()
        if 'hashed_password' not in existing_cols:
            op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
        if 'is_active' not in existing_cols:
            op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))

    # --- 2. user_preferences ---
    if "user_preferences" not in existing_tables:
        op.create_table(
            'user_preferences',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('preferred_transport', sa.String(), nullable=True),
            sa.Column('travel_style', sa.String(), nullable=True),
            sa.Column('budget_preference', sa.Float(), nullable=True),
            sa.Column('hotel_preference', sa.String(), nullable=True),
            sa.Column('activity_preferences', sa.JSON(), nullable=True),
            sa.Column('food_preferences', sa.JSON(), nullable=True),
            sa.Column('default_currency', sa.String(), nullable=False, server_default='INR'),
            sa.Column('default_output_detail', sa.String(), nullable=False, server_default='standard'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', name='uq_user_preference_user_id'),
        )
        op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=False)

    # --- 3. travel_requests ---
    if "travel_requests" not in existing_tables:
        op.create_table(
            'travel_requests',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('raw_request', sa.Text(), nullable=False),
            sa.Column('origin', sa.String(), nullable=True),
            sa.Column('destination', sa.String(), nullable=True),
            sa.Column('departure_date', sa.String(), nullable=True),
            sa.Column('return_date', sa.String(), nullable=True),
            sa.Column('travelers', sa.Integer(), nullable=True),
            sa.Column('budget', sa.Float(), nullable=True),
            sa.Column('currency', sa.String(), nullable=False, server_default='INR'),
            sa.Column('travel_style', sa.String(), nullable=True),
            sa.Column('preferred_transport', sa.JSON(), nullable=True),
            sa.Column('interests', sa.JSON(), nullable=True),
            sa.Column('accommodation_preference', sa.String(), nullable=True),
            sa.Column('output_detail', sa.String(), nullable=False, server_default='standard'),
            sa.Column('additional_requirements', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_travel_requests_user_id'), 'travel_requests', ['user_id'], unique=False)

    # --- 4. travel_runs ---
    if "travel_runs" not in existing_tables:
        op.create_table(
            'travel_runs',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('request_id', sa.String(), nullable=False),
            sa.Column('status', sa.String(), nullable=False, server_default='pending'),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('error', sa.Text(), nullable=True),
            sa.Column('final_plan', sa.JSON(), nullable=True),
            sa.Column('agent_states', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['request_id'], ['travel_requests.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_travel_runs_request_id'), 'travel_runs', ['request_id'], unique=False)

    # --- 5. transport_options ---
    if "transport_options" not in existing_tables:
        op.create_table(
            'transport_options',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('run_id', sa.String(length=36), nullable=False),
            sa.Column('mode', sa.String(), nullable=False),
            sa.Column('provider', sa.String(), nullable=False),
            sa.Column('provider_type', sa.String(), nullable=False),
            sa.Column('origin', sa.String(), nullable=False),
            sa.Column('destination', sa.String(), nullable=False),
            sa.Column('departure_time', sa.String(), nullable=True),
            sa.Column('arrival_time', sa.String(), nullable=True),
            sa.Column('duration_minutes', sa.Integer(), nullable=True),
            sa.Column('price_per_person', sa.Float(), nullable=False),
            sa.Column('total_price', sa.Float(), nullable=False),
            sa.Column('stops', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('comfort_level', sa.String(), nullable=True),
            sa.Column('vehicle_info', sa.String(), nullable=True),
            sa.Column('availability', sa.String(), nullable=False, server_default='unknown'),
            sa.Column('source', sa.String(), nullable=False),
            sa.Column('source_type', sa.String(), nullable=False),
            sa.Column('retrieved_at', sa.DateTime(), nullable=False),
            sa.Column('is_selected', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('score', sa.Float(), nullable=True),
            sa.Column('decision_factors', sa.JSON(), nullable=True),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['run_id'], ['travel_runs.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_transport_options_run_id'), 'transport_options', ['run_id'], unique=False)

    # --- 6. accommodation_options ---
    if "accommodation_options" not in existing_tables:
        op.create_table(
            'accommodation_options',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('run_id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('location', sa.String(), nullable=False),
            sa.Column('accommodation_type', sa.String(), nullable=False),
            sa.Column('rating', sa.Float(), nullable=True),
            sa.Column('nightly_price', sa.Float(), nullable=False),
            sa.Column('total_price', sa.Float(), nullable=False),
            sa.Column('amenities', sa.JSON(), nullable=True),
            sa.Column('room_type', sa.String(), nullable=True),
            sa.Column('source', sa.String(), nullable=False),
            sa.Column('source_type', sa.String(), nullable=False),
            sa.Column('availability', sa.String(), nullable=False, server_default='unknown'),
            sa.Column('retrieved_at', sa.DateTime(), nullable=False),
            sa.Column('is_selected', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['run_id'], ['travel_runs.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_accommodation_options_run_id'), 'accommodation_options', ['run_id'], unique=False)

    # --- 7. activities ---
    if "activities" not in existing_tables:
        op.create_table(
            'activities',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('run_id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('category', sa.String(), nullable=False),
            sa.Column('location', sa.String(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
            sa.Column('estimated_cost', sa.Float(), nullable=True),
            sa.Column('best_time', sa.String(), nullable=True),
            sa.Column('weather_dependency', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('source', sa.String(), nullable=False),
            sa.Column('source_type', sa.String(), nullable=False),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['run_id'], ['travel_runs.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_activities_run_id'), 'activities', ['run_id'], unique=False)

    # --- 8. itineraries ---
    if "itineraries" not in existing_tables:
        op.create_table(
            'itineraries',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('run_id', sa.String(length=36), nullable=False),
            sa.Column('title', sa.String(), nullable=True),
            sa.Column('summary', sa.Text(), nullable=True),
            sa.Column('total_days', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['run_id'], ['travel_runs.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_itineraries_run_id'), 'itineraries', ['run_id'], unique=True)

    # --- 9. itinerary_days ---
    if "itinerary_days" not in existing_tables:
        op.create_table(
            'itinerary_days',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('itinerary_id', sa.String(length=36), nullable=False),
            sa.Column('day_number', sa.Integer(), nullable=False),
            sa.Column('date', sa.String(), nullable=True),
            sa.Column('theme', sa.String(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['itinerary_id'], ['itineraries.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_itinerary_days_itinerary_id'), 'itinerary_days', ['itinerary_id'], unique=False)

    # --- 10. itinerary_items ---
    if "itinerary_items" not in existing_tables:
        op.create_table(
            'itinerary_items',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('day_id', sa.String(length=36), nullable=False),
            sa.Column('time_start', sa.String(), nullable=True),
            sa.Column('time_end', sa.String(), nullable=True),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('item_type', sa.String(), nullable=False),
            sa.Column('estimated_cost', sa.Float(), nullable=True),
            sa.Column('location', sa.String(), nullable=True),
            sa.Column('notes', sa.String(), nullable=True),
            sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['day_id'], ['itinerary_days.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_itinerary_items_day_id'), 'itinerary_items', ['day_id'], unique=False)

    # --- 11. memory_entries ---
    if "memory_entries" not in existing_tables:
        op.create_table(
            'memory_entries',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('run_id', sa.String(), nullable=True),
            sa.Column('memory_type', sa.String(), nullable=False),
            sa.Column('key', sa.String(), nullable=False),
            sa.Column('value', sa.JSON(), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_memory_entries_key'), 'memory_entries', ['key'], unique=False)
        op.create_index(op.f('ix_memory_entries_run_id'), 'memory_entries', ['run_id'], unique=False)
        op.create_index(op.f('ix_memory_entries_user_id'), 'memory_entries', ['user_id'], unique=False)

    # --- 12. agent_events ---
    if "agent_events" not in existing_tables:
        op.create_table(
            'agent_events',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('run_id', sa.String(length=36), nullable=False),
            sa.Column('agent_name', sa.String(), nullable=False),
            sa.Column('event_type', sa.String(), nullable=False),
            sa.Column('message', sa.String(), nullable=True),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('duration_ms', sa.Integer(), nullable=True),
            sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['run_id'], ['travel_runs.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_agent_events_agent_name'), 'agent_events', ['agent_name'], unique=False)
        op.create_index(op.f('ix_agent_events_run_id'), 'agent_events', ['run_id'], unique=False)

    # --- 13. llm_usage_records ---
    if "llm_usage_records" not in existing_tables:
        op.create_table(
            'llm_usage_records',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=True),
            sa.Column('request_id', sa.String(), nullable=True),
            sa.Column('run_id', sa.String(), nullable=True),
            sa.Column('agent_name', sa.String(), nullable=False),
            sa.Column('provider', sa.String(), nullable=False, server_default='groq'),
            sa.Column('model', sa.String(), nullable=False),
            sa.Column('provider_requests', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('prompt_tokens', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('completion_tokens', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('estimated_cost_usd', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('duration_ms', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('status', sa.String(), nullable=False, server_default='success'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_llm_usage_records_agent_name'), 'llm_usage_records', ['agent_name'], unique=False)
        op.create_index(op.f('ix_llm_usage_records_request_id'), 'llm_usage_records', ['request_id'], unique=False)
        op.create_index(op.f('ix_llm_usage_records_run_id'), 'llm_usage_records', ['run_id'], unique=False)
        op.create_index(op.f('ix_llm_usage_records_user_id'), 'llm_usage_records', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table('llm_usage_records')
    op.drop_table('agent_events')
    op.drop_table('memory_entries')
    op.drop_table('itinerary_items')
    op.drop_table('itinerary_days')
    op.drop_table('itineraries')
    op.drop_table('activities')
    op.drop_table('accommodation_options')
    op.drop_table('transport_options')
    op.drop_table('travel_runs')
    op.drop_table('travel_requests')
    op.drop_table('user_preferences')
    op.drop_table('users')

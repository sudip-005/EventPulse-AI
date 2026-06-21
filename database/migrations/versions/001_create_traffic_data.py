"""Create traffic_data table

Revision ID: 001_traffic_data
Revises: None
Create Date: 2026-06-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'traffic_data',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('road_id', sa.String(100), nullable=False, index=True),
        sa.Column('event_id', UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('congestion_score', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('vehicle_density', sa.Float, nullable=True),
        sa.Column('average_speed_kmh', sa.Float, nullable=True),
        sa.Column('delay_minutes', sa.Float, nullable=True),
        sa.Column('vehicle_count', sa.Integer, nullable=True),
        sa.Column('is_incident', sa.Boolean, server_default='false'),
        sa.Column('is_road_closed', sa.Boolean, server_default='false'),
        sa.Column('source', sa.String(50), server_default='forecast'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_traffic_data_road_id', 'traffic_data', ['road_id'])
    op.create_index('ix_traffic_data_event_id', 'traffic_data', ['event_id'])


def downgrade():
    op.drop_index('ix_traffic_data_event_id', table_name='traffic_data')
    op.drop_index('ix_traffic_data_road_id', table_name='traffic_data')
    op.drop_table('traffic_data')

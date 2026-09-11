"""Migration: Create sources table - Sprint 76.4.

Создание таблицы для хранения информации об источниках с метриками качества.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import func

def upgrade():
    """Create sources table."""
    op.create_table(
        'sources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('canonical_url', sa.String(500), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source_type', sa.String(50), default='rss'),
        sa.Column('language', sa.String(10), default='ru'),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('capabilities', postgresql.JSON, default=[]),
        sa.Column('topics', postgresql.JSON, default=[]),
        sa.Column('quality_score', sa.Float(), default=50.0),
        sa.Column('success_count', sa.Integer(), default=0),
        sa.Column('failure_count', sa.Integer(), default=0),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('selection_count', sa.Integer(), default=0),
        sa.Column('last_selected_at', sa.DateTime(), nullable=True),
        sa.Column('last_successful_fetch_at', sa.DateTime(), nullable=True),
        sa.Column('last_failed_fetch_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('validation_status', sa.String(50), default='unknown'),
        sa.Column('disabled_reason', sa.String(), nullable=True),
        sa.Column('discovered_from', sa.String(50), nullable=True),
        sa.Column('discovered_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('platform_metadata', postgresql.JSON, default={}),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('health_checked_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('canonical_url'),
    )

    # Create indices
    op.create_index('ix_sources_canonical_url', 'sources', ['canonical_url'])
    op.create_index('ix_sources_language', 'sources', ['language'])
    op.create_index('ix_sources_category', 'sources', ['category'])
    op.create_index('ix_sources_is_active', 'sources', ['is_active'])
    op.create_index('ix_sources_language_category', 'sources', ['language', 'category'])
    op.create_index('ix_sources_quality_score_active', 'sources', ['quality_score', 'is_active'])
    op.create_index('ix_sources_last_selected', 'sources', ['last_selected_at'])


def downgrade():
    """Drop sources table."""
    op.drop_index('ix_sources_last_selected')
    op.drop_index('ix_sources_quality_score_active')
    op.drop_index('ix_sources_language_category')
    op.drop_index('ix_sources_is_active')
    op.drop_index('ix_sources_category')
    op.drop_index('ix_sources_language')
    op.drop_index('ix_sources_canonical_url')
    op.drop_table('sources')

#!/usr/bin/env python
"""Test: Create and query a failure"""
import sys
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.pipeline_failure_orm import PipelineFailure
from datetime import datetime

db = SessionLocal()

# Create a test failure
failure = PipelineFailure(
    channel_id="test-ch-001",
    pipeline="research",
    job="fetch_sources",
    error_type="timeout",
    error_message="Test failure: timeout after 30s",
    attempt=1,
    max_attempts=3,
)

db.add(failure)
db.commit()
db.refresh(failure)

print(f'OK: Created failure {failure.id}')
print(f'  Channel: {failure.channel_id}')
print(f'  Error: {failure.error_type} - {failure.error_message}')
print(f'  Retryable: {failure.is_retryable()}')

# Query it back
all_failures = db.query(PipelineFailure).all()
print(f'OK: Total failures in DB = {len(all_failures)}')

db.close()

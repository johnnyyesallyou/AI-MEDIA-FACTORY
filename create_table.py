#!/usr/bin/env python
"""Create pipeline_failures table"""
import sys
sys.path.insert(0, '/app')

from core.database import engine
from core.models.pipeline_failure_orm import PipelineFailure
from sqlalchemy import inspect

print('Creating pipeline_failures table...')
PipelineFailure.__table__.create(engine, checkfirst=True)
print('OK: Table created')

tables = inspect(engine).get_table_names()
print(f'OK: pipeline_failures exists = {"pipeline_failures" in tables}')

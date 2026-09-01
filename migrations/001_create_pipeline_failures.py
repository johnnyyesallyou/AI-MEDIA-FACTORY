"""
Sprint 66.5: Database Migration - Create pipeline_failures table
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from core.database import Base, engine
from core.models.pipeline_failure_orm import PipelineFailure

def create_tables():
    """Create all tables in the database"""
    print("Creating pipeline_failures table...")
    
    # Create only PipelineFailure table (in case others already exist)
    PipelineFailure.__table__.create(engine, checkfirst=True)
    
    print("✅ pipeline_failures table created successfully")

if __name__ == "__main__":
    try:
        create_tables()
        print("✅ Migration completed")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

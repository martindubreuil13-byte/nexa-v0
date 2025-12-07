from typing import List, Optional, Dict
from sqlmodel import Field, SQLModel, create_engine
from sqlalchemy import Column
from sqlalchemy.types import JSON
import json

# Database setup
sqlite_file_name = "nexa.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

class Expert(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    headline: str
    rate: float
    links: List[str] = Field(default=[], sa_column=Column(JSON))
    
    # AI-derived fields
    # Using JSON column for list and dict storage in SQLite
    domains: List[str] = Field(default=[], sa_column=Column(JSON))
    icp_focus: str
    strength_mix: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    confidence_score: int = Field(ge=0, le=100)
    mini_case_response: str
    vetting_summary: str

class SMENeed(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    core_pain: str
    budget_band: str
    desired_outcome: str

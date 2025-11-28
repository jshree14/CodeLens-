"""
MongoDB models for CodeLens AI
Stores code analysis results and user review history
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class AnalysisIssue(BaseModel):
    """Individual code issue detected during analysis"""
    title: str
    description: str
    severity: str  # error, warning, info
    suggestion: str
    source: str  # static, ai


class AnalysisMetrics(BaseModel):
    """Code metrics from static analysis"""
    lines: int
    functions: int
    classes: int = 0
    loops: int = 0
    conditions: int = 0
    complexity: int


class AnalysisSummary(BaseModel):
    """AI-generated analysis summary"""
    purpose: str
    overview: str
    score: int  # 0-100 quality score


class CodeAnalysisResult(BaseModel):
    """Complete analysis result document"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code_snippet: str
    language: str
    summary: AnalysisSummary
    issues: List[AnalysisIssue]
    metrics: AnalysisMetrics
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None  # For future user authentication
    session_id: Optional[str] = None  # For grouping related analyses

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AnalysisHistory(BaseModel):
    """User's analysis history summary"""
    total_analyses: int
    languages_used: List[str]
    average_score: float
    recent_analyses: List[CodeAnalysisResult]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DatabaseConfig(BaseModel):
    """Database configuration"""
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "codelens_ai"
    collection_name: str = "analysis_results"
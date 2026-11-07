"""Pydantic request/response schemas for the FastAPI backend."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript"]

class CodeRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str
    allow_risky: bool = False
    model: str = "qwen2.5-coder:7b"
    expected_behavior: Optional[str] = None

class RefactorRequest(CodeRequest):
    goal: str = Field(default="Improve readability, maintainability, efficiency and error handling.")
    model: str = "qwen2.5-coder:7b"
    max_attempts: int = Field(default=3, ge=1, le=3)

class ValidationResponse(BaseModel):
    success: bool
    output: str
    safety: Dict[str, Any]
    code: str = ""
    issues: List[str] = []
    issue_history: List[Dict[str, Any]] = []
    summary: str = ""
    attempts: int = 1

class AnalyzeResponse(BaseModel):
    metrics: Dict[str, Any]

class RefactorResponse(BaseModel):
    success: bool
    code: str
    language: str
    attempts: int
    metadata: Dict[str, Any]
    history: List[Dict[str, Any]]
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    comparison: Dict[str, Any]

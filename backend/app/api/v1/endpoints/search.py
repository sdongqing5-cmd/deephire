"""Search endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.candidate import Candidate
from app.services.search_service import search_service

router = APIRouter()


class SearchFilters(BaseModel):
    """Search filters"""
    status: Optional[str] = None
    location: Optional[str] = None
    min_experience: Optional[int] = None


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    filters: Optional[SearchFilters] = None
    search_type: str = "hybrid"  # bm25, vector, hybrid
    size: int = 20


class SearchResult(BaseModel):
    """Search result"""
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    current_company: Optional[str]
    current_title: Optional[str]
    years_of_experience: Optional[int]
    location: Optional[str]
    status: str
    tags: List[str]
    score: float
    search_type: str
    bm25_score: Optional[float] = None
    vector_score: Optional[float] = None
    combined_score: Optional[float] = None


class SearchResponse(BaseModel):
    """Search response"""
    success: bool
    query: str
    total: int
    results: List[SearchResult]


@router.post("/candidates", response_model=SearchResponse)
async def search_candidates(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search candidates using natural language or keywords

    Supports three search types:
    - bm25: Keyword-based full-text search
    - vector: Semantic search using embeddings
    - hybrid: Combined BM25 + vector search (recommended)

    Examples:
    - "找做过医疗器械销售的人"
    - "Python后端工程师 有微服务经验"
    - "Senior Frontend Engineer React TypeScript"
    """
    # Convert filters to dict
    filters_dict = None
    if request.filters:
        filters_dict = request.filters.model_dump(exclude_none=True)

    try:
        if request.search_type == "bm25":
            results = search_service.bm25_search(
                query=request.query,
                filters=filters_dict,
                size=request.size,
            )
        elif request.search_type == "vector":
            results = search_service.vector_search(
                query=request.query,
                filters=filters_dict,
                size=request.size,
            )
        else:
            results = search_service.hybrid_search(
                query=request.query,
                filters=filters_dict,
                size=request.size,
            )
    except Exception:
        query_text = f"%{request.query}%"
        query = db.query(Candidate).filter(
            or_(
                Candidate.name.ilike(query_text),
                Candidate.email.ilike(query_text),
                Candidate.phone.ilike(query_text),
                Candidate.current_company.ilike(query_text),
                Candidate.current_title.ilike(query_text),
                Candidate.location.ilike(query_text),
            )
        )
        if filters_dict:
            if filters_dict.get("status"):
                query = query.filter(Candidate.status == filters_dict["status"])
            if filters_dict.get("location"):
                query = query.filter(Candidate.location == filters_dict["location"])
            if filters_dict.get("min_experience") is not None:
                query = query.filter(Candidate.years_of_experience >= filters_dict["min_experience"])

        results = [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone,
                "current_company": candidate.current_company,
                "current_title": candidate.current_title,
                "years_of_experience": candidate.years_of_experience,
                "location": candidate.location,
                "status": candidate.status,
                "tags": candidate.tags or [],
                "score": 1.0,
                "search_type": "database",
            }
            for candidate in query.limit(request.size).all()
        ]

    return SearchResponse(
        success=True,
        query=request.query,
        total=len(results),
        results=results,
    )


@router.get("/test")
async def test_search():
    """Test search endpoint"""
    return {
        "message": "Search service is ready",
        "index": "candidates",
        "search_types": ["bm25", "vector", "hybrid"],
    }

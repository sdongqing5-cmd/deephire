"""Search endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

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
async def search_candidates(request: SearchRequest):
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

    # Execute search based on type
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
    else:  # hybrid
        results = search_service.hybrid_search(
            query=request.query,
            filters=filters_dict,
            size=request.size,
        )

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

"""Outbound call endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.outbound_call_service import outbound_call_service

router = APIRouter()


class CallScriptRequest(BaseModel):
    """Call script generation request"""
    candidate_name: str
    job_title: str
    company_name: str
    recruiter_name: str
    candidate_background: Optional[str] = None


class ConversationRequest(BaseModel):
    """Conversation simulation request"""
    script: dict
    candidate_responses: List[str]


@router.post("/generate-script")
async def generate_call_script(request: CallScriptRequest):
    """
    Generate personalized outbound call script

    This generates an AI-powered call script for contacting candidates.
    The script includes:
    - Professional opening
    - Key selling points about the position
    - Questions to gauge interest
    - Appropriate closing

    Note: This is for script generation only. Actual phone calls
    require proper telecommunications licensing.
    """
    result = outbound_call_service.generate_call_script(
        candidate_name=request.candidate_name,
        job_title=request.job_title,
        company_name=request.company_name,
        recruiter_name=request.recruiter_name,
        candidate_background=request.candidate_background,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to generate script")
        )

    return result


@router.post("/simulate-conversation")
async def simulate_conversation(request: ConversationRequest):
    """
    Simulate AI-powered conversation

    This simulates a conversation between recruiter and candidate
    based on the generated script and candidate responses.

    Returns:
    - Full conversation history
    - Interest level analysis
    - Recommended next steps

    Note: This is a simulation tool for training and preparation.
    Actual calls require proper licensing.
    """
    result = outbound_call_service.simulate_conversation(
        script=request.script,
        candidate_responses=request.candidate_responses,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to simulate conversation")
        )

    return result


@router.get("/test")
async def test_outbound_call():
    """Test outbound call service"""
    return {
        "message": "Outbound call service is ready",
        "features": [
            "AI script generation",
            "Conversation simulation",
            "Interest level analysis"
        ],
        "note": "Actual phone calls require telecommunications licensing"
    }

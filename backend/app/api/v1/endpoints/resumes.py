"""Resume parsing endpoints"""

from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid

from app.services.resume_parser import resume_parser
from app.db.database import get_db
from app.models import Candidate as CandidateModel

router = APIRouter()


@router.post("/parse")
async def parse_resume(
    file: UploadFile = File(...),
    auto_create_candidate: bool = False,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Parse resume file and extract structured information

    Args:
        file: Resume file (PDF or DOCX)
        auto_create_candidate: If True, automatically create candidate from parsed data
        db: Database session

    Returns:
        Parsed resume data
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = file.filename.lower().split(".")[-1]
    if file_ext not in ["pdf", "docx", "doc"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF and DOCX are supported.",
        )

    try:
        # Read file content
        file_content = await file.read()

        # Parse resume
        parsed_data = resume_parser.parse_resume(file_content, file.filename)

        # Auto-create candidate if requested
        if auto_create_candidate:
            candidate = CandidateModel(
                id=str(uuid.uuid4()),
                name=parsed_data.get("name", "Unknown"),
                email=parsed_data.get("email"),
                phone=parsed_data.get("phone"),
                current_company=parsed_data.get("current_company"),
                current_title=parsed_data.get("current_title"),
                years_of_experience=parsed_data.get("years_of_experience"),
                location=parsed_data.get("location"),
                status="new",
                tags=parsed_data.get("skills", []),
                source="resume_upload",
                resume_url=parsed_data.get("resume_url"),
            )

            db.add(candidate)
            db.commit()
            db.refresh(candidate)

            parsed_data["candidate_id"] = candidate.id
            parsed_data["candidate_created"] = True

        return {
            "success": True,
            "data": parsed_data,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}",
        )


@router.post("/upload")
async def upload_resume(
    candidate_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Upload resume for existing candidate

    Args:
        candidate_id: Candidate ID
        file: Resume file
        db: Database session

    Returns:
        Upload result
    """
    # Check if candidate exists
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = file.filename.lower().split(".")[-1]
    if file_ext not in ["pdf", "docx", "doc"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF and DOCX are supported.",
        )

    try:
        # Read and save file
        file_content = await file.read()
        file_path = resume_parser.save_file(file_content, file.filename)

        # Update candidate resume URL
        candidate.resume_url = file_path
        db.commit()

        return {
            "success": True,
            "message": "Resume uploaded successfully",
            "resume_url": file_path,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload resume: {str(e)}",
        )

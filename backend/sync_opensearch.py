"""Sync candidates from PostgreSQL to OpenSearch"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.database import SessionLocal
from app.models import Candidate
from app.services.search_service import search_service


def sync_candidates():
    """Sync all candidates to OpenSearch"""
    print("\n=== Syncing Candidates to OpenSearch ===\n")

    # Create index
    print("Creating OpenSearch index...")
    search_service.create_index()

    # Get all candidates from database
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        print(f"\nFound {len(candidates)} candidates in database")

        # Index each candidate
        for i, candidate in enumerate(candidates, 1):
            candidate_data = {
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
                "summary": f"{candidate.current_title} at {candidate.current_company}",
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None,
            }

            search_service.index_candidate(candidate_data)
            print(f"  [{i}/{len(candidates)}] Indexed: {candidate.name}")

        print(f"\n✓ Successfully synced {len(candidates)} candidates to OpenSearch\n")

    except Exception as e:
        print(f"\n✗ Error during sync: {e}\n")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    sync_candidates()

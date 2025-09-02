from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from datetime import date
from src.database import get_db
from src.auth.auth_services import require_role
from src.journals.journal_schemas import JournalCreate, JournalUpdate, JournalOut
from src.journals.journal_services import create_journal, get_journal_by_id, get_user_journals, update_journal, delete_journal, get_all_journals, get_admin_journal_by_id



router = APIRouter(
    prefix = "/journals",
    tags = ["Journals"]
)


db_dependency = Annotated[Session, Depends(get_db)]


# ------------------ USER ROUTES ------------------ #

# Create Journal
@router.post("/", response_model=JournalOut, status_code=status.HTTP_201_CREATED)
def create_journal_route(db: db_dependency, journal_data: JournalCreate, current=Depends(require_role(["user"]))):
    return create_journal(db, journal_data, current.id)



# Get Current User Journals
@router.get("/me", response_model=list[JournalOut], status_code=status.HTTP_200_OK)
def get_my_journals(db: db_dependency, current=Depends(require_role(["user"])), date_filter: Optional[date] = Query(
    default=None, alias="date", description="Filter journals by creation date (format: YYYY-MM-DD)", examples={"sample": {"summary": "Example date", "value": "2025-08-26"}})
    ):

    return get_user_journals(db, current.id, date_filter)



# Get Journal by ID
@router.get("/{journal_id}", response_model=JournalOut, status_code=status.HTTP_200_OK)
def get_journal(db: db_dependency, journal_id: int, current=Depends(require_role(["user"]))):
    return get_journal_by_id(db, journal_id)



# Update Journal
@router.put("/{journal_id}", response_model=JournalOut, status_code=status.HTTP_200_OK)
def update_journal_route(db: db_dependency, journal_id: int, journal_data: JournalUpdate, current=Depends(require_role(["user"]))):
    return update_journal(db, journal_id, journal_data)



# Delete Journal
@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_route(db: db_dependency, journal_id: int, current=Depends(require_role(["user"]))):
    delete_journal(db, journal_id)
    return



# ------------------ ADMIN ROUTES ------------------ #

@router.get("/admin/", response_model=List[JournalOut], status_code=status.HTTP_200_OK)
def list_all_journals(db: db_dependency, current=Depends(require_role(["admin"]))):
    return get_all_journals(db)



@router.get("/admin/{journal_id}", response_model=JournalOut, status_code=status.HTTP_200_OK)
def get_single_journal_admin(db: db_dependency, journal_id: int, current=Depends(require_role(["admin"]))):
    return get_admin_journal_by_id(db, journal_id)
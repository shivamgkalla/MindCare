from sqlalchemy.orm import Session
from sqlalchemy import Date
from fastapi import HTTPException, status
from datetime import datetime, date
from typing import List, Optional
from src.journals.journal_models import Journal
from src.journals.journal_schemas import JournalCreate, JournalUpdate



def create_journal(db: Session, journal_data: JournalCreate, user_id: int) -> Journal:
    new_journal = Journal(
        user_id = user_id,
        title = journal_data.title,
        content = journal_data.content,
        image_url = journal_data.image_url,
    )

    db.add(new_journal)
    db.commit()
    db.refresh(new_journal)
    return new_journal



def get_journal_by_id(db: Session, journal_id: int) -> Journal:
    journal = db.query(Journal).filter(Journal.id == journal_id).first()

    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")

    return journal



def get_user_journals(db: Session, user_id: int, filter_date: Optional[date] = None) -> List[Journal]:
    query = db.query(Journal).filter(Journal.user_id == user_id)

    if filter_date:
        query = query.filter(Journal.created_at.cast(Date) == filter_date)

    return query.order_by(Journal.created_at.desc()).all()



def update_journal(db: Session, journal_id: int, journal_data: JournalUpdate, user_id: int) -> Journal:
    journal = get_journal_by_id(db, journal_id)

    if journal.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this journal")

    if journal.title is not None:
        journal.title = journal_data.title or journal.title

    if journal.content is not None:
        journal.content = journal_data.content or journal.content

    journal.updated_date = datetime.now()

    db.commit()
    db.refresh(journal)
    return journal



def delete_journal(db: Session, journal_id: int, user_id: int):
    journal = get_journal_by_id(db, journal_id)

    if journal.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this journal")

    db.delete(journal)
    db.commit()
    return {"detail": "Journal deleted successfully"}



# ------------------ ADMIN SERVICES ------------------ #

def get_all_journals(db: Session) -> List[Journal]:
    """Admin: list all journals"""
    return db.query(Journal).order_by(Journal.created_at.desc()).all()


def get_admin_journal_by_id(db: Session, journal_id: int) -> Journal:
    """Admin: view single journal"""
    return get_journal_by_id(db, journal_id)
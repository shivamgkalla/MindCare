from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from starlette.status import HTTP_404_NOT_FOUND
from src.psych_tests.psych_models import PsychTest, PsychOption, PsychQuestion, PsychUserResponse
from src.psych_tests.psych_schemas import (
    PsychTestCreateAdmin,
    PsychTestUpdateAdmin,
    PsychTestOutAdmin,
    PsychUserResponseCreate,
    PsychQuestionCreateAdmin,
    PsychOptionCreateAdmin,
    PsychQuestionUpdateAdmin,
    PsychOptionUpdateAdmin,
)


# ---------- Test CRUD (Admin) ----------
# ---------- Create Test (Admin only) ----------
def create_test_admin(db: Session, test_in: PsychTestCreateAdmin) -> PsychTest:
    new_test = PsychTest(title=test_in.title, description=test_in.description)

    # Add questions + options
    for q in test_in.questions:
        new_question = PsychQuestion(text=q.text)

        for opt in q.options:
            new_option = PsychOption(text=opt.text, is_correct=opt.is_correct or False)
            new_question.options.append(new_option)
        new_test.questions.append(new_question)

    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test



# ---------- Read Tests (Admin only) ----------
def get_test_admin(db: Session, test_id: int) -> PsychTest:
    test = db.query(PsychTest).filter(PsychTest.id == test_id).first()
    
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    
    return test



def get_all_tests_admin(db: Session) -> List[PsychTest]:
    return db.query(PsychTest).all()



# ---------- Update Test (Admin only) ----------
def update_test_admin(db: Session, test_id: int, test_in: PsychTestCreateAdmin) -> PsychTest:
    test = db.query(PsychTest).filter(PsychTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

     # Update basic fields
    test.title = test_in.title
    test.description = test_in.description

    # Clear existing questions/options before replacing
    for q in test.questions:
        db.delete(q)
    db.flush()

    # Add new questions/options
    for q in test_in.questions:
        new_question = PsychQuestion(text=q.text, test_id=test.id)
        for opt in q.options:
            new_option = PsychOption(text=opt.text, is_correct=opt.is_correct or False)
            new_question.options.append(new_option)

        db.add(new_question)

    db.commit()
    db.refresh(test)
    return test



# ---------- Patch Test (Admin only) ----------
def patch_test_admin(db: Session, test_id: int, test_in: PsychTestUpdateAdmin):
    test = db.query(PsychTest).filter(PsychTest.id == test_id).first()

    if not test:
        raise HTTPException(status_code=status>HTTP_404_NOT_FOUND, detail=f"Psychometric test with id {test_id} not found")

    # Apply only provided fields
    update_data = test_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)

    db.add(test)
    db.commit()
    db.refresh(test)
    return test


# ---------- Delete Test (Admin only) ----------
def delete_test_admin(db: Session, test_id: int) -> None:
    test = db.query(PsychTest).filter(PsychTest.id == test_id).first()
    
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    
    db.delete(test)
    db.commit()



# ---------- Question CRUD (Admin) ----------
def add_question_admin(db: Session, test_id: int, q_in: PsychQuestionCreateAdmin) -> PsychQuestion:
    test = db.query(PsychTest).filter(PsychTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")

    new_question = PsychQuestion(text=q_in.text, test_id=test.id)
    for opt in q_in.options:
        new_option = PsychOption(text=opt.text, is_correct=opt.is_correct or False)
        new_question.options.append(new_option)

    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question


def update_question_admin(db: Session, question_id: int, q_in: PsychQuestionUpdateAdmin) -> PsychQuestion:
    question = db.query(PsychQuestion).filter(PsychQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    # Only update text if provided
    if q_in.text is not None:
        question.text = q_in.text


    db.commit()
    db.refresh(question)
    return question


def delete_question_admin(db: Session, question_id: int) -> None:
    question = db.query(PsychQuestion).filter(PsychQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    db.delete(question)
    db.commit()



# ---------- Option CRUD (Admin) ----------
def add_option_admin(db: Session, question_id: int, opt_in: PsychOptionCreateAdmin) -> PsychOption:
    question = db.query(PsychQuestion).filter(PsychQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    new_option = PsychOption(text=opt_in.text, is_correct=opt_in.is_correct or False, question_id=question.id)
    db.add(new_option)
    db.commit()
    db.refresh(new_option)
    return new_option


def update_option_admin(db: Session, option_id: int, opt_in: PsychOptionUpdateAdmin) -> PsychOption:
    option = db.query(PsychOption).filter(PsychOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")

    if opt_in.text is not None:
        option.text = opt_in.text

    if opt_in.is_correct is not None:
        option.is_correct = opt_in.is_correct

    db.commit()
    db.refresh(option)
    return option


def delete_option_admin(db: Session, option_id: int) -> None:
    option = db.query(PsychOption).filter(PsychOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")

    db.delete(option)
    db.commit()



# ---------- User-facing ----------
def get_test_user(db: Session, test_id: int) -> PsychTest:
    test = db.query(PsychTest).filter(PsychTest.id == test_id).first()

    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

    return test



def get_all_tests_user(db: Session) -> List[PsychTest]:
    return db.query(PsychTest).all()



def submit_response(db: Session, user_id: int, response_in: PsychUserResponseCreate) -> PsychUserResponse:
    # Validate that question & option belong to the test
    question = db.query(PsychQuestion).filter(PsychQuestion.id == response_in.question_id).first()

    if not question or question.test_id != response_in.test_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question for this test.")

    option = db.query(PsychOption).filter(PsychOption.id == response_in.option_id).first()

    if not option or option.question_id != response_in.question_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid option for this question.")


    new_response = PsychUserResponse(
        user_id=user_id,
        test_id=response_in.test_id,
        question_id=response_in.question_id,
        option_id=response_in.option_id,
    )

    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    return new_response



def get_user_responses(db: Session, user_id: int, test_id: int) -> List[PsychUserResponse]:

    return db.query(PsychUserResponse).filter(PsychUserResponse.user_id == user_id, PsychUserResponse.test_id == test_id).all()
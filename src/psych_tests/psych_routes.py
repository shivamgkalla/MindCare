from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from src.psych_tests import psych_services as services, psych_schemas as schemas
from src.database import get_db
from src.auth.auth_services import require_role



router = APIRouter(
    prefix = "/psych-tests",
    tags = ["Psychometric Tests"]
)


db_dependency = Annotated[Session, Depends(get_db)]



# ------------------ Admin Routes ------------------


# Create a new test
@router.post("/", response_model=schemas.PsychTestOutAdmin, status_code=status.HTTP_201_CREATED)
def create_test(db: db_dependency, test_in: schemas.PsychTestCreateAdmin, current=Depends(require_role(["admin"]))):
    test = services.create_test_admin(db, test_in)
    return test



# Get all tests
@router.get("/", response_model=List[schemas.PsychTestOutAdmin], status_code=status.HTTP_200_OK)
def list_all_tests(db: db_dependency, current=Depends(require_role(["admin"]))):
    return services.get_all_tests_admin(db)



# Get a single test
@router.get("/{test_id}", response_model=schemas.PsychTestOutAdmin, status_code=status.HTTP_200_OK)
def get_test(db: db_dependency, test_id: int, current=Depends(require_role(["admin"]))):
    return services.get_test_admin(db, test_id)



# Update Test
@router.put("/{test_id}", response_model=schemas.PsychTestOutAdmin, status_code=status.HTTP_200_OK)
def update_test(db: db_dependency, test_id: int, test_in: schemas.PsychTestCreateAdmin, current=Depends(require_role(["admin"]))):
    return services.update_test_admin(db, test_id, test_in)



# Update Test (Partial Update)
@router.patch("/{test_id}", response_model=schemas.PsychTestOutAdmin, status_code=status.HTTP_200_OK)
def patch_test(db: db_dependency, test_id: int, test_in: schemas.PsychTestUpdateAdmin, current=Depends(require_role(["admin"]))):
    """
    Partially update a psychometric test (admin only).
    Only provided fields will be updated.
    """
    return services.patch_test_admin(db, test_id, test_in)



# Delete Test
@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(db: db_dependency, test_id: int, current=Depends(require_role(["admin"]))):
    services.delete_test_admin(db, test_id)
    return



# ------------------ Question Routes (Admin) ------------------

# Add question to a test
@router.post("/{test_id}/questions", response_model=schemas.PsychQuestionOutAdmin)
def add_question(db: db_dependency, test_id: int, q_in: schemas.PsychQuestionCreateAdmin, current=Depends(require_role(["admin"]))):
    return services.add_question_admin(db, test_id, q_in)



# Update a question
@router.patch("/questions/{question_id}", response_model=schemas.PsychQuestionOutAdmin, status_code=status.HTTP_200_OK)
def update_question(db: db_dependency, question_id: int, q_in: schemas.PsychQuestionUpdateAdmin, current=Depends(require_role(["admin"]))):
    return services.update_question_admin(db, question_id, q_in)



# Delete a question
@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(db: db_dependency, question_id: int, current=Depends(require_role(["admin"]))):
    services.delete_question_admin(db, question_id)
    return



# ------------------ Option Routes (Admin) ------------------

# Add option to a question
@router.post("/questions/{question_id}/options", response_model=schemas.PsychOptionOutAdmin)
def add_option(db: db_dependency, question_id: int, opt_in: schemas.PsychOptionCreateAdmin, current=Depends(require_role(["admin"]))):
    return services.add_option_admin(db, question_id, opt_in)



# Update an option
@router.patch("/options/{option_id}", response_model=schemas.PsychOptionOutAdmin)
def update_option(db: db_dependency, option_id: int, opt_in: schemas.PsychOptionUpdateAdmin, current=Depends(require_role(["admin"]))):
    return services.update_option_admin(db, option_id, opt_in)



# Delete an option
@router.delete("/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_option(db: db_dependency, option_id: int, current=Depends(require_role(["admin"]))):
    services.delete_option_admin(db, option_id)
    return



# ------------------ User Routes ------------------

# Get a single test (user view)
@router.get("/user/{test_id}", response_model=schemas.PsychTestOutUser, status_code=status.HTTP_200_OK)
def get_test_user_route(db: db_dependency, test_id: int, current=Depends(require_role(["user"]))):
    return services.get_test_user(db, test_id)



# List all tests (user view)
@router.get("/user", response_model=List[schemas.PsychTestOutUser], status_code=status.HTTP_200_OK)
def list_tests_user(db: db_dependency, current=Depends(require_role(["admin"]))):
    return services.get_all_tests_user(db)



# Submit a response
@router.post("/user/responses", response_model=schemas.PsychUserResponseOut, status_code=status.HTTP_200_OK)
def submit_response(db: db_dependency, response_in: schemas.PsychUserResponseCreate, current=Depends(require_role(["user"]))):
    return services.submit_response(db, user_id=current.id, response_in=response_in)



# Get user responses for a test
@router.get("/user/{test_id}/responses", response_model=List[schemas.PsychUserResponseOut])
def get_user_responses(db: db_dependency, test_id: int, current=Depends(require_role(["user"]))):
    return services.get_user_responses(db, user_id=current.id, test_id=test_id)
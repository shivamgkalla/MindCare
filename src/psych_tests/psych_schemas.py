from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------- Option ----------
class PsychOptionBase(BaseModel):
    text: str


# Admin can set is_correct
class PsychOptionCreateAdmin(PsychOptionBase):
    is_correct: Optional[bool] = False


class PsychOptionUpdateAdmin(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None


class PsychOptionOutAdmin(PsychOptionBase):
    id: int
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


# User-facing options (no is_correct)
class PsychOptionOutUser(PsychOptionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)



#---------- Question ----------
class PsychQuestionBase(BaseModel):
    text: str

    
class PsychQuestionCreateAdmin(PsychQuestionBase):
    options: List[PsychOptionCreateAdmin]


class PsychQuestionUpdateAdmin(BaseModel):
    text: Optional[str] = None


class PsychQuestionOutAdmin(PsychQuestionBase):
    id: int
    options: List[PsychOptionOutAdmin]

    model_config = ConfigDict(from_attributes=True)


# User sees only options without is_correct
class PsychQuestionOutUser(PsychQuestionBase):
    id: int
    options: List[PsychOptionOutUser]

    model_config = ConfigDict(from_attributes=True)


# ---------- Test ----------
class PsychTestBase(BaseModel):
    title: str
    description: Optional[str] = None


# Admin create
class PsychTestCreateAdmin(PsychTestBase):
    questions: List[PsychQuestionCreateAdmin]


class PsychTestUpdateAdmin(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class PsychTestOutAdmin(PsychTestBase):
    id: int
    questions: List[PsychQuestionOutAdmin]

    model_config = ConfigDict(from_attributes=True)


class PsychTestOutUser(PsychTestBase):
    id: int
    questions: List[PsychQuestionOutUser]


    model_config = ConfigDict(from_attributes=True)


# ---------- User Responses ----------
class PsychUserResponseBase(BaseModel):
    test_id: int
    question_id: int
    option_id: int


class PsychUserResponseCreate(PsychUserResponseBase):
    pass


class PsychUserResponseOut(PsychUserResponseBase):
    id: int
    user_id: int


    model_config = ConfigDict(from_attributes=True)



# ---------- Bulk Test Submission ----------

# ---------- Single Response ----------
class PsychSingleResponse(BaseModel):
    question_id: int = Field(..., description="ID of the question")
    option_id: int = Field(..., description="ID of the selected option")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": 5,
                "option_id": 3
            }
        }


# ---------- Bulk Submission ----------
class PsychBulkResponseCreate(BaseModel):
    test_id: int = Field(..., description="ID of the test being submitted")
    responses: List[PsychSingleResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "test_id": 2,
                "responses": [
                    {"question_id": 1, "option_id": 3},
                    {"question_id": 2, "option_id": 6},
                    {"question_id": 3, "option_id": 9}
                ]
            }
        }


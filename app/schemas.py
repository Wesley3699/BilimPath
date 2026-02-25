from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from app.models.models import UserRole
from typing import List


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    invite_code: Optional[str] = None #student code
    institution_code: Optional[str] = None 

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AnswerSubmission(BaseModel):
    question_index: int
    selected_option: str

class ExamSubmitRequest(BaseModel):
    answers: List[AnswerSubmission]

class TopicProgress(BaseModel):
    id: UUID
    title: str
    order_num: int
    mastery_level: float
    attempts_count: int

class SubjectProgress(BaseModel):
    id: UUID
    name: str
    topics: List[TopicProgress]
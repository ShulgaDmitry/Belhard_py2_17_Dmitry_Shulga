from pydantic import BaseModel, ConfigDict

class UserAdd(BaseModel):
    name: str
    age: int
    phone: str | None = None
    
class User(UserAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
class UserId(BaseModel):
    id: int

class QuizAdd(BaseModel):
    name: str
    user_id: int

class Quiz(QuizAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class QuizId(BaseModel):
    id: int

class QuizQuestionAdd(BaseModel):
    id: int
    question_ids: list[int]

class QuizQuestion(QuizQuestionAdd):
    id: int
    question_ids: list[int]
    model_config = ConfigDict(from_attributes=True)

class QuestionAdd(BaseModel):
    question: str
    answer: str
    wrong1: str
    wrong2: str
    wrong3: str

class Question(QuestionAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class QuestionId(BaseModel):
    id: int
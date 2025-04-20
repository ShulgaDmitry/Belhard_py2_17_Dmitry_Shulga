from typing import Dict, List, Any

from fastapi import APIRouter, Depends, HTTPException
from schema import *
from database import UserRepository as ur
from database import QuizRepository as quizr
from database import QuestionRepository as questionr

user_router = APIRouter(
    prefix="/users", # слэш оставляем открытыми
    tags=['Пользователи']
)

quiz_router = APIRouter(
    prefix="/quizes",
    tags=['Квизы']
)

question_router = APIRouter(
    prefix="/questions",
    tags=['Вопросы']
)

default_router = APIRouter()

@default_router.get('/', tags=['api'])
async def index():
    return {'data':'ok'}


@user_router.get('')
async def get_users() -> list[User]:
    users = await ur.get_users()
    return users

@user_router.get('/{id}')
async def get_user(id) -> User:
    user = await ur.get_user(id=id)
    if user:
        return user
    # return {'err':"User not found"} # но тогда get_user(id) -> User | dict[str,str]
    raise HTTPException(status_code=404, detail="User not found")

@user_router.post('')
async def get_user(user:UserAdd = Depends()) -> UserId:
    id = await ur.add_user(user)
    return {'id':id}



@quiz_router.get('')
async def get_quizes() -> list[Quiz]:
    quizes = await quizr.get_quizes()
    return quizes

@quiz_router.get('/{id}')
async def get_quiz(id) -> dict[str, Any]:
    quiz = await quizr.get_quiz(id=id)
    if quiz:
        question_ids = [q.id for q in quiz.questions]
        return {'id': quiz.id, 'name': quiz.name, 'user_id': quiz.user_id, 'question_ids': question_ids}
    # return {'err':"User not found"} # но тогда get_user(id) -> User | dict[str,str]
    raise HTTPException(status_code=404, detail="User not found")

@quiz_router.post('')
async def get_quiz(quiz:QuizAdd = Depends()) -> QuizId:
    id = await quizr.add_quiz(quiz)
    return {'id':id}

@quiz_router.post('{id}/questions')
async def get_quiz_questions(quiz: QuizQuestionAdd = Depends()) -> QuizQuestion:
    await quizr.add_questions_to_quiz(quiz)
    return quiz



@question_router.get('')
async def get_questions() -> list[Question]:
    questions = await questionr.get_questions()
    return questions

@question_router.get('/{id}')
async def get_question(id) -> Question:
    question = await questionr.get_question(id=id)
    if question:
        return question
    # return {'err':"User not found"} # но тогда get_user(id) -> User | dict[str,str]
    raise HTTPException(status_code=404, detail="User not found")

@question_router.post('')
async def get_question(question:QuestionAdd = Depends()) -> QuestionId:
    id = await questionr.add_question(question)
    return {'id':id}
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import select, Integer, ForeignKey, String, Table, Column, func


from schema import UserAdd, QuizAdd, QuestionAdd, QuizQuestionAdd
from datetime import datetime

import os

BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, 'db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
    
DB_PATH = os.path.join(DB_DIR, 'HW_10.db')

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
# engine = create_async_engine("sqlite+aiosqlite:///example//HW_10//db//HW_10.db")
# engine = create_async_engine("sqlite+aiosqlite:///db//HW_10.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass
    
#    # можно тут добавить тогда эти столбцы будут во всех таблицах
#    # т.к. мы наследуемся от этого класса
    
#     id: Mapped[int] = mapped_column(primary_key=True)
    
#     # будет вписывать дататайм при создании записи
#     dateCreate: Mapped[datetime] = mapped_column(        
#                                         server_default=func.now(),
#                                         nullable=False)
    
#     # будет вписывать дататайм при обновлении записи
#     dateUpdate: Mapped[datetime] = mapped_column(        
#                                         server_default=func.now(),
#                                         server_onupdate=func.now(),
#                                         nullable=False)

quizes_questions = Table(
    "quizes_questions",
    Model.metadata,  # обязательно, чтобы таблица была создана вместе с остальными
    Column("quiz_id", ForeignKey("quizes.id"), primary_key=True),
    Column("question_id", ForeignKey("questions.id"), primary_key=True)
)


class UserOrm(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    phone: Mapped[str|None]
    quiz = relationship('QuizOrm', back_populates='user')

class QuizOrm(Model):
    __tablename__ = 'quizes'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user = relationship('UserOrm', back_populates='quiz')
    questions = relationship(
        'QuestionOrm',
        secondary=quizes_questions,
        back_populates='quizes'
    )

class QuestionOrm(Model):
    __tablename__ = 'questions'
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str]
    answer: Mapped[str]
    wrong1: Mapped[str]
    wrong2: Mapped[str]
    wrong3: Mapped[str]
    quizes = relationship(
        'QuizOrm',
        secondary=quizes_questions,
        back_populates='questions'
    )

    
async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
        
async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)     


async def add_test_data():
    async with new_session() as session:
        users = [
            UserOrm(name='user1', age=20),
            UserOrm(name='user2', age=30, phone='123456789')
        ]
        quizes = [
            QuizOrm(name='test_quiz1', user_id=1),
            QuizOrm(name='test_quiz2', user_id=2)
        ]
        questions = [
            QuestionOrm(question='test_question1', answer='answer1', wrong1='w11', wrong2='w12', wrong3='w13'),
            QuestionOrm(question='rest_question2', answer='answer2', wrong1='w21', wrong2='w22', wrong3='w23')
        ]

        session.add_all(users)
        session.add_all(quizes)
        session.add_all(questions)
        await session.flush()
        await session.commit()


class UserRepository:
    
    @classmethod           
    async def add_user(cls, user: UserAdd) -> int:
        async with new_session() as session:
            data = user.model_dump()
            print(data)
            user = UserOrm(**data)
            session.add(user)
            await session.flush()
            await session.commit()
            return user.id
            
    @classmethod
    async def get_users(cls) -> list[UserOrm]:
        async with new_session() as session:
            query = select(UserOrm)
            res = await session.execute(query)
            users = res.scalars().all()
            return users
            
    @classmethod
    async def get_user(cls, id) -> UserOrm:
        async with new_session() as session:
            query = select(UserOrm).filter(UserOrm.id==id)
            # query = text(f"SELECT * FROM users WHERE id={id}")
            res = await session.execute(query) 
            user = res.scalars().first()
            return user

class QuizRepository:

    @classmethod
    async def add_quiz(cls, quiz: QuizAdd) -> int:
        async with new_session() as session:
            data = quiz.model_dump()
            print(data)
            quiz = QuizOrm(**data)
            session.add(quiz)
            await session.flush()
            await session.commit()
            return quiz.id

    @classmethod
    async def get_quizes(cls) -> list[QuizOrm]:
        async with new_session() as session:
            query = select(QuizOrm)
            res = await session.execute(query)
            quizes = res.scalars().all()
            return quizes

    @classmethod
    async def get_quiz(cls, id) -> QuizOrm:
        async with new_session() as session:
            query = select(QuizOrm).options(selectinload(QuizOrm.questions)).filter(QuizOrm.id == id)
            res = await session.execute(query)
            quiz = res.scalars().first()
            return quiz

    @classmethod
    async def add_questions_to_quiz(cls, quiz_question: QuizQuestionAdd) -> QuizOrm:
        async with new_session() as session:
            quiz = await session.get(QuizOrm, quiz_question.id, options=[selectinload(QuizOrm.questions)])
            if not quiz:
                raise ValueError(f"Quiz with id={quiz_question.id} not found")

            stmt = select(QuestionOrm).where(QuestionOrm.id.in_(quiz_question.question_ids))
            res = await session.execute(stmt)
            questions = res.scalars().all()

            quiz.questions.extend(questions)
            await session.commit()
            return quiz

class QuestionRepository:

    @classmethod
    async def add_question(cls, question: QuestionAdd) -> int:
        async with new_session() as session:
            data = question.model_dump()
            print(data)
            question = QuestionOrm(**data)
            session.add(question)
            await session.flush()
            await session.commit()
            return question.id

    @classmethod
    async def get_questions(cls) -> list[QuestionOrm]:
        async with new_session() as session:
            query = select(QuestionOrm)
            res = await session.execute(query)
            questions = res.scalars().all()
            return questions

    @classmethod
    async def get_question(cls, id) -> QuestionOrm:
        async with new_session() as session:
            query = select(QuestionOrm).filter(QuestionOrm.id == id)
            res = await session.execute(query)
            question = res.scalars().first()
            return question
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import os
import logging
from config import DATABASE_URL  # Import the DATABASE_URL from config.py

app = FastAPI()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    options = relationship("Option", back_populates="question")

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="options")

Base.metadata.create_all(bind=engine)

class OptionCreate(BaseModel):
    text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    text: str
    options: list[OptionCreate]

class OptionResponse(BaseModel):
    id: int
    text: str
    is_correct: bool

class QuestionResponse(BaseModel):
    id: int
    text: str
    options: list[OptionResponse]

    class Config:
        orm_mode = True

class AnswerSubmission(BaseModel):
    answers: dict

class DetailedResult(BaseModel):
    question_id: int
    question_text: str
    selected_options: list[int]
    correct_options: list[int]
    correct_options_text: list[str]

class ResultResponse(BaseModel):
    score: int
    detailed_results: list[DetailedResult]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/questions/")
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(text=question.text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for option in question.options:
        db_option = Option(text=option.text, is_correct=option.is_correct, question_id=db_question.id)
        db.add(db_option)
    db.commit()
    return db_question

@app.get("/questions/", response_model=list[QuestionResponse])
def read_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions

@app.post("/submit-answers/", response_model=ResultResponse)
def submit_answers(answers: dict, db: Session = Depends(get_db)):
    logging.info(f"Received answers: {answers}")
    score = 0
    detailed_results = []
    for question_key, selected_option_ids in answers.items():
        question_id = int(question_key.split('-')[1])
        logging.info(f"Processing question_id: {question_id}, selected_option_ids: {selected_option_ids}")
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            logging.error(f"Question not found for id: {question_id}")
            continue
        correct_options = [option.id for option in question.options if option.is_correct]
        correct_options_text = [option.text for option in question.options if option.is_correct]
        logging.info(f"Correct options for question_id {question_id}: {correct_options}")
        logging.info(f"Selected options for question_id {question_id}: {selected_option_ids}")
        if set(correct_options) == set(map(int, selected_option_ids)):
            score += 1
        detailed_results.append({
            "question_id": question.id,
            "question_text": question.text,
            "selected_options": list(map(int, selected_option_ids)),
            "correct_options": correct_options,
            "correct_options_text": correct_options_text
        })
    logging.info(f"Final score: {score}")
    return {"score": score, "detailed_results": detailed_results}

@app.post("/tests/{test_id}/submit-answers/")
def submit_answers(test_id: int, answers: dict, db: Session = Depends(get_db)):
    score = 0
    detailed_results = []
    for question_key, selected_option_ids in answers.items():
        question_id = int(question_key.split('-')[1])
        question = db.query(Question).filter(Question.id == question_id, Question.test_id == test_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
        correct_options = [option.id for option in question.options if option.is_correct]
        correct_options_text = [option.text for option in question.options if option.is_correct]
        selected_options = db.query(Option).filter(Option.id.in_([int(option_id) for option_id in selected_option_ids])).all()
        selected_options_text = [option.text for option in selected_options]
        if set(correct_options) == set(map(int, selected_option_ids)):
            score += 1
        detailed_results.append({
            "question_text": question.text,
            "selected_options": selected_options_text,
            "correct_options": correct_options_text
        })
    return {"score": score, "detailed_results": detailed_results}

@app.get("/tests/")
def get_tests(db: Session = Depends(get_db)):
    tests = db.query(Test).all()
    return tests

@app.get("/tests/{test_id}/questions/", response_model=list[QuestionResponse])
def get_questions(test_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    for question in questions:
        question.options  # This will trigger the lazy loading of options
    return questions

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join("templates", "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Serve results.html
@app.get("/results.html", response_class=HTMLResponse)
async def read_results():
    try:
        with open(os.path.join("templates", "results.html")) as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        logging.error(f"Error serving results.html: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Lesson, QuizQuestion, Progress

app = FastAPI(title="Study App API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_str_id(doc: dict):
    if not doc:
        return doc
    d = doc.copy()
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

# Root
@app.get("/")
def read_root():
    return {"message": "Study App Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# API Models for requests
class LessonCreate(Lesson):
    pass

class QuizCreate(QuizQuestion):
    pass

class ProgressCreate(Progress):
    pass

# Endpoints
@app.post("/lessons", response_model=dict)
def create_lesson(payload: LessonCreate):
    lesson_id = create_document("lesson", payload)
    return {"id": lesson_id}

@app.get("/lessons", response_model=List[dict])
def list_lessons(grade: Optional[int] = None, subject: Optional[str] = None):
    filter_dict = {}
    if grade is not None:
        filter_dict["grade"] = grade
    if subject is not None:
        filter_dict["subject"] = subject
    docs = get_documents("lesson", filter_dict=filter_dict)
    return [to_str_id(d) for d in docs]

@app.get("/lessons/{lesson_id}", response_model=dict)
def get_lesson(lesson_id: str):
    try:
        doc = db["lesson"].find_one({"_id": ObjectId(lesson_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return to_str_id(doc)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lesson id")

@app.post("/quizzes", response_model=dict)
def create_quiz_question(payload: QuizCreate):
    # ensure lesson exists
    try:
        _ = db["lesson"].find_one({"_id": ObjectId(payload.lesson_id)})
        if _ is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lesson id")
    qid = create_document("quizquestion", payload)
    return {"id": qid}

@app.get("/quizzes", response_model=List[dict])
def list_quiz_questions(lesson_id: Optional[str] = None):
    filter_dict = {}
    if lesson_id:
        try:
            filter_dict["lesson_id"] = lesson_id
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid lesson id")
    docs = get_documents("quizquestion", filter_dict=filter_dict)
    return [to_str_id(d) for d in docs]

@app.post("/progress", response_model=dict)
def set_progress(payload: ProgressCreate):
    pid = create_document("progress", payload)
    return {"id": pid}

@app.get("/progress", response_model=List[dict])
def get_progress(student: Optional[str] = None, lesson_id: Optional[str] = None):
    filter_dict = {}
    if student:
        filter_dict["student"] = student
    if lesson_id:
        filter_dict["lesson_id"] = lesson_id
    docs = get_documents("progress", filter_dict=filter_dict)
    return [to_str_id(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

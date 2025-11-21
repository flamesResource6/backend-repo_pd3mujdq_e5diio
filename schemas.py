"""
Database Schemas for Study App (Grades 5-9)

Each Pydantic model represents a MongoDB collection.
Collection name = lowercase class name.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class Lesson(BaseModel):
    """
    Lessons for a given grade and subject
    Collection: "lesson"
    """
    grade: int = Field(..., ge=1, le=12, description="School grade")
    subject: str = Field(..., description="Subject name, e.g., Math, Science, English")
    title: str = Field(..., description="Lesson title")
    content: str = Field(..., description="Lesson content in markdown/plain text")
    video_url: Optional[str] = Field(None, description="Optional video link")

class QuizQuestion(BaseModel):
    """
    Quiz questions attached to a lesson
    Collection: "quizquestion"
    """
    lesson_id: str = Field(..., description="Associated lesson _id as string")
    question: str
    options: List[str] = Field(..., min_length=2, max_length=6)
    correct_index: int = Field(..., ge=0, le=5)

class Progress(BaseModel):
    """
    Student progress per lesson
    Collection: "progress"
    """
    student: Optional[str] = Field(None, description="Student name or identifier")
    lesson_id: str
    completed: bool = False
    score: Optional[int] = Field(None, ge=0, le=100)

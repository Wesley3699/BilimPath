from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone

from app.dependencies import get_db, get_current_user
from app.models.models import User, Topic, Subject, LearningSession, Exam, SessionStatus
from app.services.ai_service import generate_quiz, analyze_errors

router = APIRouter(prefix="/exams", tags=["Exams"])

# Схема для запроса
class GenerateExamRequest(BaseModel):
    topic_id: str
    difficulty: int = 3

@router.post("/generate")
async def create_ai_exam(
    request: GenerateExamRequest, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Topic).where(Topic.id == request.topic_id))
    topic = res.scalars().first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    session_res = await db.execute(
        select(LearningSession).where(
            LearningSession.student_id == current_user.id,
            LearningSession.subject_id == topic.subject_id,
            LearningSession.status == SessionStatus.testing
        )
    )
    learning_session = session_res.scalars().first()
    
    if not learning_session:
        learning_session = LearningSession(
            student_id=current_user.id,
            subject_id=topic.subject_id,
            status=SessionStatus.testing
        )
        db.add(learning_session)
        await db.flush()

    try:
        questions_json = await generate_quiz(topic_name=topic.title, difficulty=request.difficulty)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации ИИ: {str(e)}")

    new_exam = Exam(
        session_id=learning_session.id,
        topic_id=topic.id,
        difficulty=request.difficulty,
        questions=questions_json
    )
    db.add(new_exam)
    await db.commit()
    await db.refresh(new_exam)

    return {
        "exam_id": new_exam.id,
        "topic": topic.title,
        "questions": new_exam.questions
    }



from app.models.models import ExamAttempt, AiAnalysis, StudentTopicMastery, AnswerType
from app.schemas import ExamSubmitRequest

@router.post("/{exam_id}/submit")
async def submit_exam(
    exam_id: uuid.UUID,
    submission: ExamSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Exam).where(Exam.id == exam_id).options(selectinload(Exam.topic)))
    exam = res.scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Тест не найден")

    questions = exam.questions
    correct_count = 0
    total_questions = len(questions)
    
    for i, q in enumerate(questions):
        user_answer = next((a.selected_option for a in submission.answers if a.question_index == i), None)
        if user_answer == q['correct_answer']:
            correct_count += 1

    score = (correct_count / total_questions) * 100


    attempt = ExamAttempt(
        exam_id=exam.id,
        student_id=current_user.id,
        answers=[a.model_dump() for a in submission.answers],
        score=score,
        answer_type=AnswerType.multiple_choice
    )
    db.add(attempt)
    await db.flush()


    mastery_res = await db.execute(
        select(StudentTopicMastery).where(
            StudentTopicMastery.student_id == current_user.id,
            StudentTopicMastery.topic_id == exam.topic_id
        )
    )
    mastery = mastery_res.scalars().first()
    
    if not mastery:
        mastery = StudentTopicMastery(
            student_id=current_user.id, 
            topic_id=exam.topic_id,
            attempts_count=0,
            mastery_level=0.0
        )
        db.add(mastery)

    if mastery.attempts_count is None:
        mastery.attempts_count = 0

    mastery.mastery_level = score 
    mastery.attempts_count += 1
    mastery.last_tested_at = datetime.now()


    try:
        analysis_data = await analyze_errors(exam.topic.title, questions, [a.model_dump() for a in submission.answers])
        ai_analysis = AiAnalysis(
            attempt_id=attempt.id,
            score=score,
            explanation=analysis_data.get("explanation"),
            weak_topics=analysis_data.get("weak_topics"),
            recommendations=analysis_data.get("recommendation")
        )
        db.add(ai_analysis)
    except Exception as e:
        print(f"AI Analysis Error: {e}")

    await db.commit()

    return {
        "score": score,
        "correct_answers": f"{correct_count}/{total_questions}",
        "analysis": analysis_data if 'analysis_data' in locals() else "Анализ временно недоступен"
    }
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.dependencies import get_db, get_current_user
from app.models.models import (
    User, UserRole, Course, Lesson, LessonProgress,
    CourseEnrollment, Topic, LearningSession, Exam, SessionStatus
)
from app.services.ai_service import generate_quiz

router = APIRouter(prefix="/courses", tags=["Courses"])

class LessonProgressOut(BaseModel):
    status: str
    progress_percent: float

class LessonOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    duration_minutes: int
    order_num: int
    is_published: bool
    video_url: Optional[str]
    content: Optional[str]
    progress: Optional[LessonProgressOut] = None

    class Config:
        from_attributes = True

class CourseOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    is_active: bool
    lessons_count: int
    enrolled: bool

    class Config:
        from_attributes = True

class CourseDetailOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    is_active: bool
    enrolled: bool
    lessons: List[LessonOut]

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None

class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: int = 0
    order_num: int = 0
    topic_id: Optional[UUID] = None

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order_num: Optional[int] = None
    is_published: Optional[bool] = None
    topic_id: Optional[UUID] = None

class LessonProgressUpdate(BaseModel):
    progress_percent: float

async def _require_teacher(current_user: User):
    if current_user.role != UserRole.teacher:
        raise HTTPException(
            status_code=403,
            detail="Только преподаватель может выполнять это действие"
        )

async def _get_course_or_404(course_id: UUID, db: AsyncSession) -> Course:
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course

async def _get_lesson_or_404(lesson_id: UUID, db: AsyncSession) -> Lesson:
    res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = res.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    return lesson

async def _is_enrolled(user_id: UUID, course_id: UUID, db: AsyncSession) -> bool:
    res = await db.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.student_id == user_id,
            CourseEnrollment.course_id == course_id,
        )
    )
    return res.scalars().first() is not None

@router.get("", response_model=List[CourseOut])
async def list_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Course)
        .where(
            Course.institution_id == current_user.institution_id,
            Course.is_active == True,
        )
        .options(selectinload(Course.lessons), selectinload(Course.enrollments))
    )
    courses = res.scalars().all()

    result = []
    for c in courses:
        enrolled = any(e.student_id == current_user.id for e in c.enrollments)
        result.append(
            CourseOut(
                id=c.id,
                title=c.title,
                description=c.description,
                is_active=c.is_active,
                lessons_count=len(c.lessons),
                enrolled=enrolled,
            )
        )
    return result

@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_teacher(current_user)

    course = Course(
        title=data.title,
        description=data.description,
        institution_id=current_user.institution_id,
        created_by=current_user.id,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)

    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        is_active=course.is_active,
        lessons_count=0,
        enrolled=False,
    )

@router.get("/{course_id}", response_model=CourseDetailOut)
async def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Course)
        .where(Course.id == course_id)
        .options(selectinload(Course.lessons))
    )
    course = res.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    enrolled = await _is_enrolled(current_user.id, course_id, db)

    progress_res = await db.execute(
        select(LessonProgress).where(LessonProgress.student_id == current_user.id)
    )
    progress_map = {p.lesson_id: p for p in progress_res.scalars().all()}

    lessons_out = []
    for lesson in sorted(course.lessons, key=lambda l: l.order_num):
        if not lesson.is_published and current_user.role == UserRole.student:
            continue

        prog = progress_map.get(lesson.id)
        lessons_out.append(
            LessonOut(
                id=lesson.id,
                title=lesson.title,
                description=lesson.description,
                duration_minutes=lesson.duration_minutes,
                order_num=lesson.order_num,
                is_published=lesson.is_published,
                video_url=lesson.video_url,
                content=lesson.content,
                progress=LessonProgressOut(
                    status=prog.status,
                    progress_percent=prog.progress_percent,
                ) if prog else None,
            )
        )

    return CourseDetailOut(
        id=course.id,
        title=course.title,
        description=course.description,
        is_active=course.is_active,
        enrolled=enrolled,
        lessons=lessons_out,
    )

@router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_course_or_404(course_id, db)

    if await _is_enrolled(current_user.id, course_id, db):
        raise HTTPException(status_code=400, detail="Вы уже записаны на этот курс")

    db.add(CourseEnrollment(course_id=course_id, student_id=current_user.id))
    await db.commit()
    return {"message": "Вы успешно записались на курс"}

@router.post("/{course_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: UUID,
    data: LessonCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_teacher(current_user)
    await _get_course_or_404(course_id, db)

    lesson = Lesson(
        course_id=course_id,
        title=data.title,
        description=data.description,
        content=data.content,
        video_url=data.video_url,
        duration_minutes=data.duration_minutes,
        order_num=data.order_num,
        topic_id=data.topic_id,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    return LessonOut(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        duration_minutes=lesson.duration_minutes,
        order_num=lesson.order_num,
        is_published=lesson.is_published,
        video_url=lesson.video_url,
        content=lesson.content,
    )

@router.patch("/{course_id}/lessons/{lesson_id}", response_model=LessonOut)
async def update_lesson(
    course_id: UUID,
    lesson_id: UUID,
    data: LessonUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_teacher(current_user)
    lesson = await _get_lesson_or_404(lesson_id, db)

    if lesson.course_id != course_id:
        raise HTTPException(status_code=400, detail="Урок не принадлежит этому курсу")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(lesson, field, value)

    await db.commit()
    await db.refresh(lesson)

    return LessonOut(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        duration_minutes=lesson.duration_minutes,
        order_num=lesson.order_num,
        is_published=lesson.is_published,
        video_url=lesson.video_url,
        content=lesson.content,
    )

@router.delete("/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    course_id: UUID,
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_teacher(current_user)
    lesson = await _get_lesson_or_404(lesson_id, db)

    if lesson.course_id != course_id:
        raise HTTPException(status_code=400, detail="Урок не принадлежит этому курсу")

    await db.delete(lesson)
    await db.commit()

@router.post("/{course_id}/lessons/{lesson_id}/progress")
async def update_lesson_progress(
    course_id: UUID,
    lesson_id: UUID,
    data: LessonProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson_or_404(lesson_id, db)

    if lesson.course_id != course_id:
        raise HTTPException(status_code=400, detail="Урок не принадлежит этому курсу")

    res = await db.execute(
        select(LessonProgress).where(
            LessonProgress.lesson_id == lesson_id,
            LessonProgress.student_id == current_user.id,
        )
    )
    progress = res.scalars().first()

    if not progress:
        progress = LessonProgress(
            lesson_id=lesson_id,
            student_id=current_user.id,
            status="in_progress",
            started_at=datetime.now(),
        )
        db.add(progress)

    progress.progress_percent = min(data.progress_percent, 100.0)
    progress.last_accessed_at = datetime.now()

    if progress.progress_percent >= 100.0:
        progress.status = "completed"
        progress.completed_at = datetime.now()
    else:
        progress.status = "in_progress"

    await db.commit()
    return {
        "lesson_id": str(lesson_id),
        "status": progress.status,
        "progress_percent": progress.progress_percent,
    }

@router.post("/{course_id}/lessons/{lesson_id}/exam")
async def generate_exam_for_lesson(
    course_id: UUID,
    lesson_id: UUID,
    difficulty: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson_or_404(lesson_id, db)

    if lesson.course_id != course_id:
        raise HTTPException(status_code=400, detail="Урок не принадлежит этому курсу")

    if current_user.role == UserRole.student:
        res = await db.execute(
            select(LessonProgress).where(
                LessonProgress.lesson_id == lesson_id,
                LessonProgress.student_id == current_user.id,
                LessonProgress.status == "completed",
            )
        )
        if not res.scalars().first():
            raise HTTPException(
                status_code=400,
                detail="Сначала завершите урок (прогресс 100%), чтобы пройти экзамен",
            )

    if not lesson.topic_id:
        raise HTTPException(
            status_code=400,
            detail="У этого урока не привязана тема (topic_id). Преподаватель должен указать topic_id при создании урока.",
        )

    topic_res = await db.execute(select(Topic).where(Topic.id == lesson.topic_id))
    topic = topic_res.scalars().first()

    if not topic:
        raise HTTPException(status_code=404, detail="Привязанная тема не найдена")

    session_res = await db.execute(
        select(LearningSession).where(
            LearningSession.student_id == current_user.id,
            LearningSession.subject_id == topic.subject_id,
            LearningSession.status == SessionStatus.testing,
        )
    )
    learning_session = session_res.scalars().first()

    if not learning_session:
        learning_session = LearningSession(
            student_id=current_user.id,
            subject_id=topic.subject_id,
            status=SessionStatus.testing,
        )
        db.add(learning_session)
        await db.flush()

    try:
        questions_json = await generate_quiz(topic_name=topic.title, difficulty=difficulty)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации AI: {str(e)}")

    exam = Exam(
        session_id=learning_session.id,
        topic_id=topic.id,
        difficulty=difficulty,
        questions=questions_json,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    return {
        "exam_id": exam.id,
        "lesson_title": lesson.title,
        "topic": topic.title,
        "questions": exam.questions,
        "submit_url": f"/exams/{exam.id}/submit",
    }
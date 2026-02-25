from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.dependencies import get_db, get_current_user
from app.models.models import User, Subject, Topic, StudentTopicMastery
from app.schemas import SubjectProgress, TopicProgress

router = APIRouter(prefix="/subjects", tags=["Subjects & Progress"])

@router.get("/my-progress", response_model=List[SubjectProgress])
async def get_my_progress(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # 1. Получаем все предметы и загружаем связанные с ними темы
    subjects_res = await db.execute(
        select(Subject).options(selectinload(Subject.topics))
    )
    subjects = subjects_res.scalars().all()

    # 2. Получаем оценки (прогресс) текущего студента
    mastery_res = await db.execute(
        select(StudentTopicMastery).where(StudentTopicMastery.student_id == current_user.id)
    )
    # Делаем словарь {topic_id: mastery_object} для быстрого поиска
    masteries = {m.topic_id: m for m in mastery_res.scalars().all()}

    # 3. Собираем красивый ответ для фронтенда
    result = []
    for subj in subjects:
        topics_data = []
        
        # Сортируем темы по порядку (order_num)
        for topic in sorted(subj.topics, key=lambda t: t.order_num):
            m = masteries.get(topic.id) # Ищем оценку студента по этой теме
            
            topics_data.append(TopicProgress(
                id=topic.id,
                title=topic.title,
                order_num=topic.order_num,
                mastery_level=m.mastery_level if m else 0.0, # Если еще не сдавал - 0
                attempts_count=m.attempts_count if m else 0
            ))
        
        result.append(SubjectProgress(
            id=subj.id,
            name=subj.name,
            topics=topics_data
        ))

    return result
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid

from app.dependencies import get_db
from app.routers import auth, exams, subjects
from app.models.models import Institution, Group

app = FastAPI(title="AI Mentor + Smart Edu Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(exams.router)
app.include_router(subjects.router)

@app.get("/")
async def root():
    return {"message": "AI is running"}

@app.get("/ping-db")
async def ping_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db_status": "connected", "result": result.scalar()}


from sqlalchemy import select
from app.models.models import Institution, Group, Subject, Topic

@app.post("/setup-demo")
async def setup_demo(db: AsyncSession = Depends(get_db)):
    # 1. Проверяем или создаем Учреждение
    res = await db.execute(select(Institution).where(Institution.short_code == "MUIT"))
    institution = res.scalars().first()
    if not institution:
        institution = Institution(name="Международный Университет", short_code="MUIT")
        db.add(institution)
        await db.flush()

    # 2. Проверяем или создаем Группу
    res = await db.execute(select(Group).where(Group.invite_code == "7H0K29"))
    group = res.scalars().first()
    if not group:
        group = Group(name="ИС-181", invite_code="7H0K29", institution_id=institution.id)
        db.add(group)
        await db.flush()

    # 3. Проверяем или создаем Предмет
    res = await db.execute(select(Subject).where(Subject.name == "Программирование на Python"))
    subject = res.scalars().first()
    if not subject:
        subject = Subject(name="Программирование на Python")
        db.add(subject)
        await db.flush()

    # 4. Проверяем или создаем Тему
    res = await db.execute(select(Topic).where(Topic.title == "Базовые типы данных (int, float, str)"))
    topic = res.scalars().first()
    if not topic:
        topic = Topic(subject_id=subject.id, title="Базовые типы данных (int, float, str)", order_num=1)
        db.add(topic)
        
    await db.commit()
    
    return {
        "message": "Демо данные готовы!",
        "institution_code": institution.short_code,
        "group_code": group.invite_code,
        "topic_id": str(topic.id) # Вот этот ID нам нужен для генерации теста!
    }
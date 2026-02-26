import asyncio
import random
import string
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.models.models import (
    Base, User, UserRole,
    Institution, Group, StudentProfile, TeacherProfile,
    Subject, Topic,
    Course, Lesson,
)
from app.security import get_password_hash


# ENGINE
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)



# HELPERS
def gen_code(n=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

# Data
INSTITUTIONS = [
    {"name": "Международный университет информационных технологий", "short_code": "MUIT"},
    {"name": "Казахстанско-Британский технический университет",      "short_code": "KBTU"},
]

TEACHERS = [
    {"full_name": "Айгуль Нурланова",  "email": "teacher@muit.kz",  "institution": "MUIT"},
    {"full_name": "Данияр Сейткали",   "email": "teacher@kbtu.kz",  "institution": "KBTU"},
]

GROUPS = [
    {"name": "ИС-181", "invite_code": "MUIT01", "institution": "MUIT"},
    {"name": "CS-202", "invite_code": "KBTU01", "institution": "KBTU"},
]

STUDENTS = [
    {"full_name": "Алибек Жаксыбеков", "email": "alibek@student.kz",  "group_code": "MUIT01"},
    {"full_name": "Дана Серикова",      "email": "dana@student.kz",    "group_code": "MUIT01"},
    {"full_name": "Нурлан Касымов",     "email": "nurlan@student.kz",  "group_code": "KBTU01"},
]

# Предметы с темами
SUBJECTS_DATA = [
    {
        "name": "Математика",
        "topics": [
            "Числа и арифметика",
            "Алгебра: уравнения и неравенства",
            "Функции и графики",
            "Производные и интегралы",
            "Теория вероятностей",
        ]
    },
    {
        "name": "Информатика и программирование",
        "topics": [
            "Основы алгоритмов",
            "Базовые типы данных (int, float, str)",
            "Условия и циклы",
            "Функции и рекурсия",
            "Структуры данных: список, словарь, множество",
            "ООП: классы и объекты",
        ]
    },
    {
        "name": "История Казахстана",
        "topics": [
            "Древние государства на территории Казахстана",
            "Казахское ханство: образование и расцвет",
            "Присоединение к Российской империи",
            "Казахстан в советский период",
            "Независимость и современное государство",
        ]
    },
    {
        "name": "Английский язык",
        "topics": [
            "Времена глаголов: Present Simple и Continuous",
            "Past Simple и Past Perfect",
            "Future Simple и Future Perfect",
            "Модальные глаголы",
            "Условные предложения (Conditionals)",
            "Пассивный залог",
        ]
    },
    {
        "name": "Физика",
        "topics": [
            "Механика: кинематика",
            "Механика: динамика и законы Ньютона",
            "Энергия, работа и мощность",
            "Электрический ток и цепи",
            "Электромагнетизм",
        ]
    },
]

# Курсы с уроками
COURSES_DATA = [
    {
        "subject": "Математика",
        "title": "Математика: базовый курс",
        "description": "Фундаментальные понятия математики для студентов первого курса",
        "lessons": [
            {
                "title": "Числа и системы счисления",
                "description": "Натуральные, целые, рациональные и иррациональные числа",
                "content": "В этом уроке мы рассмотрим основные типы чисел и их свойства. Натуральные числа используются для счёта, целые числа расширяют натуральные на отрицательные значения. Рациональные числа выражаются в виде дроби p/q, где q≠0. Иррациональные числа нельзя выразить в виде дроби — например, √2 и число π.",
                "duration_minutes": 45,
                "topic_index": 0,
            },
            {
                "title": "Линейные уравнения",
                "description": "Решение уравнений вида ax + b = 0",
                "content": "Линейное уравнение — это уравнение первой степени. Общий вид: ax + b = 0. Решение: x = -b/a. Пример: 3x + 9 = 0 → x = -3. Важно проверять ответ подстановкой в исходное уравнение.",
                "duration_minutes": 60,
                "topic_index": 1,
            },
            {
                "title": "Квадратные уравнения",
                "description": "Формула дискриминанта и способы решения",
                "content": "Квадратное уравнение: ax² + bx + c = 0. Дискриминант D = b² - 4ac. Если D > 0 — два корня, D = 0 — один корень, D < 0 — нет вещественных корней. Корни: x = (-b ± √D) / 2a.",
                "duration_minutes": 60,
                "topic_index": 1,
            },
        ]
    },
    {
        "subject": "Информатика и программирование",
        "title": "Python с нуля",
        "description": "Полный курс программирования на Python для начинающих",
        "lessons": [
            {
                "title": "Введение в Python",
                "description": "Установка, первая программа, синтаксис",
                "content": "Python — интерпретируемый язык программирования высокого уровня. Установка: python.org. Первая программа: print('Hello, World!'). Python использует отступы вместо фигурных скобок. Комментарии начинаются с символа #.",
                "duration_minutes": 45,
                "topic_index": 0,
            },
            {
                "title": "Переменные и типы данных",
                "description": "int, float, str, bool — основные типы",
                "content": "Переменные в Python не требуют объявления типа. Основные типы: int (целые числа), float (дробные числа), str (строки), bool (True/False). Функция type() показывает тип переменной. Преобразование типов: int('5'), str(42), float(3).",
                "duration_minutes": 50,
                "topic_index": 1,
            },
            {
                "title": "Условия: if / elif / else",
                "description": "Ветвление логики программы",
                "content": "Условный оператор if проверяет условие. Синтаксис: if условие: / elif другое_условие: / else:. Операторы сравнения: ==, !=, >, <, >=, <=. Логические операторы: and, or, not. Важно соблюдать отступы (4 пробела).",
                "duration_minutes": 55,
                "topic_index": 2,
            },
            {
                "title": "Циклы: for и while",
                "description": "Повторение действий в программе",
                "content": "Цикл for перебирает элементы: for i in range(10). Цикл while выполняется пока условие истинно: while x > 0. break прерывает цикл, continue переходит к следующей итерации. range(start, stop, step) генерирует последовательность чисел.",
                "duration_minutes": 60,
                "topic_index": 2,
            },
            {
                "title": "Функции в Python",
                "description": "Определение и вызов функций, аргументы, return",
                "content": "Функция определяется через def имя(параметры):. Оператор return возвращает значение. Аргументы по умолчанию: def greet(name='World'):. Функции помогают избежать повторения кода (принцип DRY). *args и **kwargs позволяют передавать произвольное количество аргументов.",
                "duration_minutes": 65,
                "topic_index": 3,
            },
        ]
    },
    {
        "subject": "История Казахстана",
        "title": "История Казахстана: от древности до наших дней",
        "description": "Ключевые этапы исторического развития Казахстана",
        "lessons": [
            {
                "title": "Саки и гунны: первые государства",
                "description": "Древние кочевые народы на территории современного Казахстана",
                "content": "Территория современного Казахстана была заселена с эпохи палеолита. Саки — ираноязычные кочевники (VII-III вв. до н.э.), создавшие первые государственные образования. Гунны — тюркоязычные племена, сыгравшие ключевую роль в великом переселении народов. Основное занятие — кочевое скотоводство.",
                "duration_minutes": 45,
                "topic_index": 0,
            },
            {
                "title": "Казахское ханство (1465 г.)",
                "description": "Образование, расцвет и ханы казахского государства",
                "content": "Казахское ханство образовано в 1465 году ханами Керей и Жанибеком. Делилось на три жуза: Старший, Средний и Младший. Золотой век — правление хана Касыма (1511-1523) и Хакназара (1538-1580). Столицы: Сыгнак, Туркестан. Основа экономики — кочевое скотоводство и транзитная торговля.",
                "duration_minutes": 50,
                "topic_index": 1,
            },
        ]
    },
    {
        "subject": "Английский язык",
        "title": "English Grammar: Intermediate",
        "description": "Грамматика английского языка для среднего уровня",
        "lessons": [
            {
                "title": "Present Simple vs Present Continuous",
                "description": "Когда и как использовать два настоящих времени",
                "content": "Present Simple используется для постоянных действий, фактов и расписаний: I work every day. Present Continuous — для действий, происходящих прямо сейчас или временных ситуаций: I am working now. Маркеры: always/usually/often/never (Simple) vs now/at the moment/currently (Continuous). Глаголы состояния (know, like, want) не используются в Continuous.",
                "duration_minutes": 50,
                "topic_index": 0,
            },
            {
                "title": "Past Simple и Past Perfect",
                "description": "Прошедшие времена и их различия",
                "content": "Past Simple — завершённое действие в прошлом: I went to school. Past Perfect — действие, завершившееся до другого прошлого действия: I had finished my homework before she called. Past Perfect образуется: had + V3. Маркеры: yesterday, ago, last year (Simple) vs already, by the time, before (Perfect).",
                "duration_minutes": 55,
                "topic_index": 1,
            },
            {
                "title": "Modal Verbs: can, must, should, may",
                "description": "Модальные глаголы: значение и использование",
                "content": "Can — способность или разрешение: I can swim. Must — обязательство или уверенность: You must stop. Should — совет: You should sleep more. May/Might — возможность: It may rain. После модальных глаголов всегда инфинитив без to (кроме ought to). Отрицание: cannot/can't, must not/mustn't.",
                "duration_minutes": 50,
                "topic_index": 3,
            },
        ]
    },
    {
        "subject": "Физика",
        "title": "Физика: механика и электричество",
        "description": "Основные разделы физики для студентов технических специальностей",
        "lessons": [
            {
                "title": "Кинематика: движение и скорость",
                "description": "Равномерное и равноускоренное движение",
                "content": "Кинематика изучает движение без учёта его причин. Скорость: v = Δx/Δt. Ускорение: a = Δv/Δt. Равноускоренное движение: x = x₀ + v₀t + at²/2, v = v₀ + at. Свободное падение: ускорение g ≈ 9.8 м/с². Графики: x(t) — положение, v(t) — скорость, a(t) — ускорение.",
                "duration_minutes": 60,
                "topic_index": 0,
            },
            {
                "title": "Законы Ньютона",
                "description": "Три закона динамики и их применение",
                "content": "1-й закон (инерции): тело покоится или движется равномерно, пока нет внешней силы. 2-й закон: F = ma — сила равна произведению массы на ускорение. 3-й закон: действие равно противодействию. Единицы: сила в Ньютонах (Н), масса в кг, ускорение в м/с².",
                "duration_minutes": 65,
                "topic_index": 1,
            },
            {
                "title": "Электрический ток: основные понятия",
                "description": "Напряжение, ток, сопротивление. Закон Ома",
                "content": "Электрический ток — направленное движение заряженных частиц. Сила тока I измеряется в Амперах. Напряжение U — в Вольтах. Сопротивление R — в Омах. Закон Ома: I = U/R. Последовательное соединение: R = R₁ + R₂. Параллельное: 1/R = 1/R₁ + 1/R₂. Мощность: P = UI = I²R.",
                "duration_minutes": 60,
                "topic_index": 3,
            },
        ]
    },
]


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================

async def seed():
    async with AsyncSessionLocal() as db:
        print("🌱 Начинаем заполнение БД...\n")

        # --- УЧРЕЖДЕНИЯ ---
        institutions = {}
        for inst_data in INSTITUTIONS:
            res = await db.execute(select(Institution).where(Institution.short_code == inst_data["short_code"]))
            inst = res.scalars().first()
            if not inst:
                inst = Institution(name=inst_data["name"], short_code=inst_data["short_code"])
                db.add(inst)
                await db.flush()
                print(f"  🏫 Создано учреждение: {inst.short_code}")
            else:
                print(f"  ✅ Учреждение уже есть: {inst.short_code}")
            institutions[inst_data["short_code"]] = inst

        # --- ПРЕПОДАВАТЕЛИ ---
        teachers = {}
        for t_data in TEACHERS:
            res = await db.execute(select(User).where(User.email == t_data["email"]))
            teacher = res.scalars().first()
            if not teacher:
                inst = institutions[t_data["institution"]]
                teacher = User(
                    email=t_data["email"],
                    password_hash=get_password_hash("teacher123"),
                    full_name=t_data["full_name"],
                    role=UserRole.teacher,
                    institution_id=inst.id,
                )
                db.add(teacher)
                await db.flush()
                db.add(TeacherProfile(user_id=teacher.id))
                await db.flush()
                print(f"  👩‍🏫 Создан преподаватель: {teacher.email} / пароль: teacher123")
            else:
                print(f"  ✅ Преподаватель уже есть: {teacher.email}")
            teachers[t_data["institution"]] = teacher

        # --- ГРУППЫ ---
        groups = {}
        for g_data in GROUPS:
            res = await db.execute(select(Group).where(Group.invite_code == g_data["invite_code"]))
            group = res.scalars().first()
            if not group:
                inst = institutions[g_data["institution"]]
                teacher = teachers[g_data["institution"]]
                group = Group(
                    name=g_data["name"],
                    invite_code=g_data["invite_code"],
                    institution_id=inst.id,
                    teacher_id=teacher.id,
                )
                db.add(group)
                await db.flush()
                print(f"  👥 Создана группа: {group.name} (код: {group.invite_code})")
            else:
                print(f"  ✅ Группа уже есть: {group.name}")
            groups[g_data["invite_code"]] = group

        # --- СТУДЕНТЫ ---
        for s_data in STUDENTS:
            res = await db.execute(select(User).where(User.email == s_data["email"]))
            student = res.scalars().first()
            if not student:
                group = groups[s_data["group_code"]]
                student = User(
                    email=s_data["email"],
                    password_hash=get_password_hash("student123"),
                    full_name=s_data["full_name"],
                    role=UserRole.student,
                    institution_id=group.institution_id,
                )
                db.add(student)
                await db.flush()
                db.add(StudentProfile(user_id=student.id, group_id=group.id))
                await db.flush()
                print(f"  🎓 Создан студент: {student.email} / пароль: student123")
            else:
                print(f"  ✅ Студент уже есть: {student.email}")

        # --- ПРЕДМЕТЫ И ТЕМЫ ---
        subjects_map = {}
        topics_map = {}  # subject_name -> [topics]

        for subj_data in SUBJECTS_DATA:
            res = await db.execute(select(Subject).where(Subject.name == subj_data["name"]))
            subject = res.scalars().first()
            if not subject:
                subject = Subject(name=subj_data["name"])
                db.add(subject)
                await db.flush()
                print(f"  📚 Создан предмет: {subject.name}")
            else:
                print(f"  ✅ Предмет уже есть: {subject.name}")
            subjects_map[subj_data["name"]] = subject

            topic_list = []
            for i, topic_title in enumerate(subj_data["topics"]):
                res = await db.execute(
                    select(Topic).where(Topic.subject_id == subject.id, Topic.title == topic_title)
                )
                topic = res.scalars().first()
                if not topic:
                    topic = Topic(subject_id=subject.id, title=topic_title, order_num=i)
                    db.add(topic)
                    await db.flush()
                topic_list.append(topic)

            topics_map[subj_data["name"]] = topic_list

        # --- КУРСЫ И УРОКИ ---
        for course_data in COURSES_DATA:
            subject = subjects_map[course_data["subject"]]
            topic_list = topics_map[course_data["subject"]]

            res = await db.execute(select(Course).where(Course.title == course_data["title"]))
            course = res.scalars().first()
            if not course:
                course = Course(
                    title=course_data["title"],
                    description=course_data["description"],
                    institution_id=list(institutions.values())[0].id,
                    is_active=True,
                )
                db.add(course)
                await db.flush()
                print(f"  📖 Создан курс: {course.title}")

                for i, lesson_data in enumerate(course_data["lessons"]):
                    topic_index = lesson_data.get("topic_index", 0)
                    topic = topic_list[topic_index] if topic_index < len(topic_list) else topic_list[0]

                    lesson = Lesson(
                        course_id=course.id,
                        topic_id=topic.id,
                        title=lesson_data["title"],
                        description=lesson_data["description"],
                        content=lesson_data["content"],
                        duration_minutes=lesson_data["duration_minutes"],
                        order_num=i,
                        is_published=True,
                    )
                    db.add(lesson)
                print(f"     └─ {len(course_data['lessons'])} уроков добавлено")
            else:
                print(f"  ✅ Курс уже есть: {course.title}")

        await db.commit()

        print("\n" + "="*50)
        print("✅ БД успешно заполнена!\n")
        print("📋 Аккаунты для тестирования:")
        print()
        print("👩‍🏫 ПРЕПОДАВАТЕЛИ:")
        for t in TEACHERS:
            print(f"   {t['email']} / teacher123  [{t['institution']}]")
        print()
        print("🎓 СТУДЕНТЫ:")
        for s in STUDENTS:
            print(f"   {s['email']} / student123  (группа: {s['group_code']})")
        print()
        print("🔑 КОДЫ ГРУПП:")
        for g in GROUPS:
            print(f"   {g['name']}: {g['invite_code']}")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(seed())
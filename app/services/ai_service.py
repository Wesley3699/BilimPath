import json
from openai import AsyncOpenAI
from app.config import settings


client = AsyncOpenAI(
    base_url=settings.LM_STUDIO_URL,
    api_key="lm-studio"
)

async def generate_quiz(topic_name: str, difficulty: int = 3) -> list:

    
    prompt = f"""
    Сгенерируй тест из 3 вопросов по теме '{topic_name}'. Уровень сложности: {difficulty} из 5.
    ОБЯЗАТЕЛЬНО ВЕРНИ ТОЛЬКО ВАЛИДНЫЙ JSON-МАССИВ. Никакого текста до или после JSON.
    Формат строго такой:
    [
      {{
        "question": "текст вопроса",
        "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
        "correct_answer": "вариант1"
      }}
    ]
    """
    
    response = await client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "system", "content": "Ты ИИ-наставник. Ты отвечаешь строго в формате JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2 
    )
    
    raw_content = response.choices[0].message.content.strip()
    

    if raw_content.startswith("```json"):
        raw_content = raw_content[7:]
    if raw_content.endswith("```"):
        raw_content = raw_content[:-3]
        
    return json.loads(raw_content.strip())


async def analyze_errors(topic_name: str, questions: list, user_answers: list) -> dict:
    
    prompt = f"""
    Студент прошел тест по теме '{topic_name}'.
    Вопросы и правильные ответы: {json.dumps(questions, ensure_ascii=False)}
    Ответы студента: {json.dumps(user_answers, ensure_ascii=False)}
    
    Найди ошибки, объясни простым языком, почему ответ неверный, и дай одну рекомендацию: что именно повторить.
    Ответ верни строго в формате JSON:
    {{
      "explanation": "общий разбор ошибок",
      "weak_topics": ["тема 1", "тема 2"],
      "recommendation": "совет студенту"
    }}
    """
    
    response = await client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content.strip())
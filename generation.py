from groq import Groq
from utils import CONFIG_FILE
from datetime import datetime

def generate_morning_message(config):
    now = datetime.now()
    day = now.strftime("%A")
    time = now.strftime("%I:%M %p")
    name = config.get("name", "пользователь")

    prompt = f"""
    генерируй в одну строку пожелания на доброе утро, так же человек должен: заботиться о себе, о внешности, о состоянии, выполнять задачи, чистить зубы и засыпать вовремя.
    Имя: {name}
    Дата: {day}
    Время: {time}
    """

    client = Groq(api_key=config.get("token"))
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "system",
                "content": prompt.strip()
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    message = ""
    for chunk in completion:
        message += chunk.choices[0].delta.content or ""
    return message
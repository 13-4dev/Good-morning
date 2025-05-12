# cython: language_level=3
import cython
from groq import Groq
from utils_cy import CONFIG_FILE, DEFAULT_PROMPTS
from datetime import datetime
import sys
from typing import Dict, Any, Generator

SYSTEM_PROMPTS = {
    "English": "You are a friendly morning assistant that provides encouraging messages in English.",
    "Russian": "Вы дружелюбный утренний ассистент, который предоставляет ободряющие сообщения на русском языке."
}

@cython.boundscheck(False)
@cython.wraparound(False)
def generate_morning_message(dict config) -> str:
    cdef:
        str day, time, name, language, prompt_template, prompt, message, error_message
    
    try:
        now = datetime.now()
        day = now.strftime("%A")
        time = now.strftime("%I:%M %p")
        name = config.get("name", "user")
        language = config.get("language", "English")
        
        if not config.get("token"):
            raise ValueError("API token is missing. Please set up your configuration first.")
        
        if not config.get("model"):
            raise ValueError("Model name is missing. Please set up your configuration first.")
        
        prompt_template = config.get("prompt", DEFAULT_PROMPTS[language])
        prompt = prompt_template.format(name=name, day=day, time=time)

        client = Groq(api_key=config.get("token"))
        
        try:
            completion = client.chat.completions.create(
                model=config.get("model", "gemma2-9b-it"),
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPTS[language]
                    },
                    {
                        "role": "user",
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
            
        except Exception as api_error:
            error_message = str(api_error)
            if "404" in error_message:
                raise ValueError(f"Model '{config.get('model')}' not found. Please check the model name and try again.")
            elif "401" in error_message:
                raise ValueError("Invalid API token. Please check your token and try again.")
            else:
                raise ValueError(f"API Error: {error_message}")
                
    except ValueError as ve:
        print(f"Error: {str(ve)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1) 
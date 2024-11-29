from ollama import Client
import json
from functools import wraps
import time

client = Client(host='http://localhost:11434')

def retry_on_json_error(max_retries=5, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except json.JSONDecodeError:
                    retries += 1
                    if retries == max_retries:
                        return {"error": f"Invalid JSON response from LLaMA after {max_retries} retries"}
                    print(f"Retry {retries}/{max_retries} due to invalid JSON response...")
                    time.sleep(delay)
            return {"error": "Unexpected error in retry mechanism"}
        return wrapper
    return decorator

@retry_on_json_error(max_retries=5)
def get_word_metadata(word: str) -> dict:
    """獲取單字的基本資料（音標、詞性、定義）"""
    prompt = f"""你現在是一個英語詞典json產生器。請提供以下英文單字的資料：
{word}

請依照以下JSON格式回覆, 不需要其他多餘的描述, 直接給我json：
{{
    "phonetic": "/kk音標/",
    "meanings": [
        {{
            "pos": "詞性",
            "definition": "該詞性中文意思",
            "examples": [
                {{
                    "en": "英文例句1(要出現該單字)",
                    "zh": "中文翻譯1"
                }},
                {{
                    "en": "英文例句2(要出現該單字)",
                    "zh": "中文翻譯2"
                }}
            ]
        }},
        // 可以有多個詞性...列出該單字所有詞性
    ]
}}

例如 'book' 的回覆：
{{
    "phonetic": "/bʊk/",
    "meanings": [
        {{
            "pos": "noun",
            "definition": "書籍",
            "examples": [
                {{
                    "en": "I bought a new book yesterday.",
                    "zh": "我昨天買了一本新書。"
                }},
                {{
                    "en": "She loves reading books.",
                    "zh": "她喜歡讀書。"
                }}
            ]
        }},
        {{
            "pos": "verb",
            "definition": "預訂",
            "examples": [
                {{
                    "en": "I need to book a flight.",
                    "zh": "我需要預訂一張機票。"
                }},
                {{
                    "en": "Have you booked the restaurant?",
                    "zh": "你預訂餐廳了嗎？"
                }}
            ]
        }}
    ]
}}"""

    response = client.generate(
        model='llama3.1:8b',
        prompt=prompt,
        stream=False
    )
    
    return json.loads(response['response'].strip()) 
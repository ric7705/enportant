from ollama import Client

client = Client(host='http://localhost:11434')

def get_word_translation(word: str) -> str:
    """獲取單字的中文翻譯"""
    prompt = f"""你現在是一個英文翻譯專家。
請將以下英文單字翻譯成最適合的繁體中文：
{word}

只需要回覆中文翻譯，不需要其他解釋。
例如輸入 'hello' 你就只要回答 '你好'"""

    response = client.generate(
        model='llama3.1:8b',
        prompt=prompt,
        stream=False
    )
    
    return response['response'].strip()

def get_sentence_translation(sentence: str) -> str:
    """獲取英文句子的中文翻譯"""
    prompt = f"""你現在是一個英文翻譯專家。
請將以下英文句子翻譯成流暢的繁體中文：
{sentence}

只需要回覆中文翻譯，不需要其他解釋。
例如輸入 'How are you?' 你就只要回答 '你好嗎？'"""

    response = client.generate(
        model='llama3.1:8b',
        prompt=prompt,
        stream=False
    )
    
    return response['response'].strip() 
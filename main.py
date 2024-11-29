from genanki import Model, Note, Deck, Package
import requests
import json
from translate_llama import get_word_metadata
import time


def get_audio_url(word, mock=False):
    """只從 dictionary API 獲取音訊 URL"""
    if mock:
        try:
            with open(f'mock/{word}.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            return ""
    else:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return ""
        
        data = response.json()

    return data[0].get('phonetics', [{}])[0].get('audio', '')


def get_word_info(word, mock=False):
    """整合 LLaMA 資料和音訊 URL"""
    # 從 LLaMA 獲取詞典資料
    word_data = get_word_metadata(word)
    if "error" in word_data:
        return word_data
    
    # 只從 API 獲取音訊 URL
    audio_url = get_audio_url(word, mock)
    
    return {
        "word": word,
        "phonetic": word_data['phonetic'],
        "audio_url": audio_url,
        "meanings": word_data['meanings']
    }


def get_template():
    model = Model(
        1607390516,
        'Word Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Phonetic'},
            {'name': 'Audio'},
            {'name': 'Content'}
        ],
        templates=[{
            'name': 'Word Card',
            'qfmt': '''
                <div>{{Word}}</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr>
                <div>
                    <div>
                        <div>{{Phonetic}}</div>
                        {{#Audio}}
                        <div>
                            <audio controls src="{{Audio}}"></audio>
                        </div>
                        {{/Audio}}
                    </div>
                    <div>{{Content}}</div>
                </div>
            ''',
            'css': ''
        }]
    )
    return model


def format_content(word_info):
    html = ""
    for i, meaning in enumerate(word_info['meanings']):
        if i > 0:
            html += '<hr>'
        
        html += f'''
            <div>
                <div>{meaning['pos']}</div>
                <div>{meaning['definition']}</div>
                <div>Examples:</div>
        '''
        
        for example in meaning['examples'][:2]:
            html += f'''
                <div>
                    <span>→</span>
                    <span>{example['en']}</span>
                    <div>{example['zh']}</div>
                </div>
            '''
            
        html += '</div></div>'
    
    return html


def process_words_from_file(filename):
    start_time = time.time()
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            words = [word.strip() for word in file.readlines() if word.strip()]
    except FileNotFoundError:
        print(f"file not found：{filename}")
        return
    
    deck = Deck(2059400516, 'High Frequency 10000 Words')
    
    for i, word in enumerate(words, 1):
        word_start_time = time.time()
        try:
            print(f"processing {i}/{len(words)}：{word}")
            word_info = get_word_info(word, mock=False)
            
            if "error" in word_info:
                print(f"processing {word} error：{word_info['error']}")
                continue
                
            note = Note(
                model=get_template(),
                fields=[
                    word,
                    word_info['phonetic'],
                    word_info['audio_url'],
                    format_content(word_info)
                ]
            )
            
            deck.add_note(note)
            word_time = time.time() - word_start_time
            print(f"added：{word} (took {word_time:.2f} seconds)")
            
        except Exception as e:
            print(f"processing {word} error：{str(e)}")
            continue
    
    package = Package(deck)
    package.write_to_file('high_frequency_10000_words.apkg')
    
    total_time = time.time() - start_time
    print(f"Done! Anki deck file generated")
    print(f"Total words processed: {len(words)}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per word: {total_time/len(words):.2f} seconds")

if __name__ == "__main__":
    process_words_from_file('word.txt')

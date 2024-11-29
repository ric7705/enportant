from genanki import Model, Note, Deck, Package
import requests
import json
from translate import Translator
from translate_llama import get_word_translation, get_sentence_translation


def get_from_dictionary(word, mock=False):
    if mock:
        try:
            with open(f'mock/{word}.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            return {"error": "Mock file not found"}
    else:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {"error": "Unable to fetch data"}
        
        data = response.json()

    word_info = []
    phonetic = data[0].get('phonetics', [{}])[0].get('text', '')
    audio_url = data[0].get('phonetics', [{}])[0].get('audio', '')
    
    for entry in data:
        for meaning in entry.get('meanings', []):
            pos = meaning.get('partOfSpeech', '')
            definitions = []
            examples = []
            
            for definition in meaning.get('definitions', []):
                definitions.append(definition.get('definition', ''))
                if definition.get('example'):
                    examples.append(definition.get('example'))
            
            word_info.append({
                'pos': pos,
                'definitions': definitions,
                'examples': examples[:2]
            })
    
    return {
        "phonetic": phonetic,
        "audio_url": audio_url,
        "meanings": word_info
    }

def get_translate_by_google_crawler(word, examples):
    translator = Translator(to_lang='zh-TW')
    
    word_translation = translator.translate(word)
    
    translated_examples = []
    for example_list in examples:
        translated_group = []
        for example in example_list:
            translated_group.append(translator.translate(example))
        translated_examples.append(translated_group)
    
    return {
        "word_translation": word_translation,
        "examples_translation": translated_examples
    }

def get_translate_by_llama(word, examples):
    """translate by llama model"""
    # translate word
    word_translation = get_word_translation(word)
    
    # translate sentence
    translated_examples = []
    for example_list in examples:
        translated_group = []
        for example in example_list:
            translated_group.append(get_sentence_translation(example))
        translated_examples.append(translated_group)
    
    return {
        "word_translation": word_translation,
        "examples_translation": translated_examples
    }


def get_translate(word, examples):
    # return get_translate_from_google_crawler(word, examples)
    return get_translate_by_llama(word, examples)


def get_word_info(word, mock=False):
    """
    get meta data from API or model
    """
    dict_info = get_from_dictionary(word, mock)
    if "error" in dict_info:
        return dict_info
    
    examples_to_translate = []
    for meaning in dict_info['meanings']:
        examples_to_translate.append(meaning['examples'])
    
    translations = get_translate(word, examples_to_translate)
    
    return {
        "word": word,
        "phonetic": dict_info['phonetic'],
        "audio_url": dict_info['audio_url'],
        "meanings": dict_info['meanings'],
        "translations": translations
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
                <div>{word_info['translations']['word_translation']}</div>
                <div>定義: {meaning['definitions'][0]}</div>
                <div>範例:</div>
        '''
        
        for j, example in enumerate(meaning['examples'][:2]):
            html += f'''
                <div>
                    <span>→</span>
                    <span>{example}</span>
                    <div>{word_info['translations']['examples_translation'][i][j]}</div>
                </div>
            '''
            
        html += '</div></div>'
    
    return html


word = "kind"
word_info = get_word_info(word, mock=True)

deck = Deck(2059400516, 'High Frequency 10000 Words')
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
package = Package(deck)
package.write_to_file('high_frequency_10000_words.apkg')

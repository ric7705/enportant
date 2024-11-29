from genanki import Model, Note, Deck, Package
import requests
import json


def get_word_info(word, mock=False):
    if mock:
        # 讀取本地JSON檔案
        try:
            with open(f'mock/{word}.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            return {"error": "Mock file not found"}
    else:
        # 呼叫API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": "Unable to fetch data"}

        data = response.json()

    word_info = []

    # 取得音標和發音
    phonetic = data[0].get('phonetics', [{}])[0].get('text', '')
    audio_url = data[0].get('phonetics', [{}])[0].get('audio', '')

    # 針對每個詞性整理資料
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
                'examples': examples[:2]  # 只取前兩個例句
            })

    return {
        "phonetic": phonetic,
        "audio_url": audio_url,
        "meanings": word_info
    }


def get_template():
    model = Model(1607390516,
                  'Word Model',
                  fields=[{
                      'name': 'Word'
                  }, {
                      'name': 'Phonetic'
                  }, {
                      'name': 'Audio'
                  }, {
                      'name': 'Meanings'
                  }],
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
                    <div>{{Meanings}}</div>
                </div>
            ''',
                      'css': ''
                  }])
    return model


def format_meanings_html(meanings):
    html = ""
    for i, meaning in enumerate(meanings):
        if i > 0:
            html += '<hr>'

        html += f'''
            <div>
                <div>{meaning['pos']}</div>
                <div>定義: {meaning['definitions'][0]}</div>
                <div>範例:</div>
        '''

        for example in meaning['examples'][:2]:
            html += f'''
                <div>
                    <span>→</span>
                    <span>{example}</span>
                </div>
            '''

        html += '</div></div>'

    return html


# 使用時：
word = "kind"
word_info = get_word_info(word, mock=True)

deck = Deck(2059400516, 'High Frequency 10000 Words')
note = Note(
    model=get_template(),
    fields=[
        word,
        word_info['phonetic'],
        word_info['audio_url'],
        format_meanings_html(word_info['meanings'])  # 使用格式化後的 HTML
    ])

deck.add_note(note)
package = Package(deck)
package.write_to_file('high_frequency_10000_words.apkg')

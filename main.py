from genanki import Model, Note, Deck, Package
import requests

def get_word_info(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Unable to fetch data"}
    
    data = response.json()
    
    phonetic = data[0].get('phonetics', [{}])[0].get('text', '')
    
    part_of_speech = ", ".join([meaning['partOfSpeech'] for meaning in data[0].get('meanings', [])])
    
    examples = []
    for meaning in data[0].get('meanings', []):
        for definition in meaning.get('definitions', []):
            example = definition.get('example', '')
            if example:
                examples.append(example)
    
    return {
        "phonetic": phonetic,
        "part of speech": part_of_speech,
        "example": examples
    }

def get_template():
    """
    return view of the card
    """
    return Model(
        1607390516,  
        'Basic Model',  
        fields=['Word', 'Part of Speech', 'Phonetic', 'Definition', 'Example 1', 'Example 2'],  # 字卡欄位
        templates=[{
            'name': 'Card',
            'qfmt': '{{Word}}',  
            'afmt': '''
                {{FrontSide}}<hr id="answer">
                詞性: {{Part of Speech}}<br>
                音標: {{Phonetic}}<br>
                定義: {{Definition}}<br>
                例句:<br>
                {{Example 1}}<br>
                {{Example 2}}<br>
            '''  
        }]
    )

deck = Deck(2059400516, 'High Frequency 10000 Words')  
note = Note(
    model=get_template(),
    fields=['Kind', 'noun', 'ˈkaɪnd', 'A type of', 'The opening served as a kind of window.', 'Kind acts are always appreciated.']  
)

deck.add_note(note)

package = Package(deck)
package.write_to_file('high_frequency_10000_words.apkg')
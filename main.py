from genanki import Model, Note, Deck, Package
import requests
import json
from translate_llama import get_word_metadata
import time
from gtts import gTTS
import os


def get_audio_url(word, mock=False):
    """Get audio URL from dictionary API only"""
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
    """Integrate LLaMA data and audio path"""
    # Get dictionary data from LLaMA
    word_data = get_word_metadata(word)
    if "error" in word_data:
        return word_data
    
    # Use local audio file path
    audio_path = f"[sound:{word}.mp3]"
    
    return {
        "word": word,
        "phonetic": word_data['phonetic'],
        "audio_url": audio_path,  # Use local audio path
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
                        <div>{{Audio}}</div>
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


def get_word_audio(word: str, output_dir: str = "audio"):
    """Generate audio file using Google TTS"""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate audio file
        tts = gTTS(word, lang='en')
        audio_path = f"{output_dir}/{word}.mp3"
        tts.save(audio_path)
        
        return audio_path
    except Exception as e:
        print(f"Error generating audio for {word}: {e}")
        exit() # exit when hit rate limit
        return None


def download_all_audios(words):
    """Download audio files for all words"""
    print("Starting audio file downloads...")
    
    # Collect existing audio files
    existing_audios = set()
    if os.path.exists("audio"):
        existing_audios = {
            f.replace(".mp3", "") 
            for f in os.listdir("audio") 
            if f.endswith(".mp3")
        }
    
    for i, word in enumerate(words, 1):
        if word in existing_audios:
            print(f"Skipping existing audio {i}/{len(words)}: {word}")
            continue
            
        print(f"Downloading audio {i}/{len(words)}: {word}")
        get_word_audio(word)
    
    print("Audio file downloads completed")


def process_words_from_file(filename):
    start_time = time.time()
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            words = [word.strip() for word in file.readlines() if word.strip()]
    except FileNotFoundError:
        print(f"file not found：{filename}")
        return
    
    # Download all audio files first
    download_all_audios(words)
    
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
                    f'[sound:{word}.mp3]',  # Use Anki sound tag format
                    format_content(word_info)
                ]
            )
            
            deck.add_note(note)
            word_time = time.time() - word_start_time
            print(f"added：{word} (took {word_time:.2f} seconds)")
            
        except Exception as e:
            print(f"processing {word} error：{str(e)}")
            continue
    
    # Create package with audio files
    package = Package(deck)
    # Add all audio files to package
    for word in words:
        audio_path = f"audio/{word}.mp3"
        if os.path.exists(audio_path):
            package.media_files.append(audio_path)
    
    package.write_to_file('high_frequency_10000_words.apkg')
    
    total_time = time.time() - start_time
    print(f"Done! Anki deck file generated")
    print(f"Total words processed: {len(words)}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per word: {total_time/len(words):.2f} seconds")

if __name__ == "__main__":
    process_words_from_file('word.txt')

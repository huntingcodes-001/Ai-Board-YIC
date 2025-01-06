import whisper
from pydub import AudioSegment
from pydub.utils import make_chunks
from googletrans import Translator
from fpdf import FPDF
import os

class CustomPDF(FPDF):
    def write_text(self, text):
        """
        Write properly aligned text, including RTL and complex scripts.
        """
        # Split text into lines
        lines = text.split("\n")
        for line in lines:
            self.multi_cell(0, 10, line, align='R' if self.is_rtl(line) else 'L')

    def is_rtl(self, text):
        """
        Determine if a text is predominantly RTL (e.g., Arabic, Urdu).
        """
        for char in text:
            if '\u0600' <= char <= '\u06FF':  # Arabic and similar scripts
                return True
        return False

def convert_webm_to_mp3(webm_path, mp3_path):
    """
    Convert a WEBM file to MP3 format.
    """
    print(f"Converting {webm_path} to {mp3_path}...")
    audio = AudioSegment.from_file(webm_path, format="webm")
    audio.export(mp3_path, format="mp3")
    print("Conversion complete.")

def transcribe_long_audio(file_path, chunk_length_seconds=30):
    """
    Transcribe long audio files by splitting them into smaller chunks.
    """
    # Load the Whisper model
    model = whisper.load_model("base")  # Use "base", "small", "medium", or "large"

    # Load the audio file
    audio = AudioSegment.from_file(file_path)
    
    # Convert chunk length to milliseconds
    chunk_length_ms = chunk_length_seconds * 1000

    # Split the audio into chunks
    chunks = make_chunks(audio, chunk_length_ms)

    # Directory to store chunks
    chunk_dir = "audio_chunks"
    os.makedirs(chunk_dir, exist_ok=True)

    # Transcribe each chunk and combine results
    transcripts = []
    for i, chunk in enumerate(chunks):
        chunk_name = os.path.join(chunk_dir, f"chunk_{i}.mp3")
        chunk.export(chunk_name, format="mp3")
        
        print(f"Transcribing chunk {i+1}/{len(chunks)}: {chunk_name}")
        result = model.transcribe(chunk_name)
        transcripts.append(result["text"])
    
    # Combine all transcripts into one
    full_transcript = " ".join(transcripts)

    # Clean up chunk files
    for chunk_file in os.listdir(chunk_dir):
        os.remove(os.path.join(chunk_dir, chunk_file))
    os.rmdir(chunk_dir)

    return full_transcript

def translate_transcript(transcript, languages):
    """
    Translate the transcript into the specified languages.
    """
    translator = Translator()
    translations = {}
    for lang_code in languages:
        print(f"Translating into {languages[lang_code]}...")
        translation = translator.translate(transcript, dest=lang_code).text
        translations[lang_code] = translation
    return translations

def save_to_pdf(filename, content, font_name, font_path, rtl=False):
    """
    Save the given content to a PDF file.
    """
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font(font_name, '', font_path, uni=True)  # Ensure proper rendering of UTF-8 text
    pdf.set_font(font_name, size=12)

    # Write content using the custom method
    pdf.write_text(content)
    pdf.output(filename)
    print(f"Saved to {filename}")

# Main function to run
if __name__ == "__main__":
    input_file = "gg.webm"  # Replace with your WEBM file path
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.getcwd(), base_filename)
    os.makedirs(output_dir, exist_ok=True)

    mp3_file = os.path.join(output_dir, "converted_audio.mp3")

    # Step 1: Convert WEBM to MP3
    convert_webm_to_mp3(input_file, mp3_file)

    # Step 2: Transcribe the MP3 file
    transcript = transcribe_long_audio(mp3_file, chunk_length_seconds=30)

    # Step 3: Save the English transcript
    eng_file = os.path.join(output_dir, f"{base_filename}-eng.pdf")
    default_font_path = os.path.join("fonts", "NotoSans-Regular.ttf")  # Default font
    save_to_pdf(eng_file, transcript, font_name="DefaultFont", font_path=default_font_path)

    # Step 4: Translate the transcript into multiple languages
    languages = {
        'hi': 'Hindi',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'bn': 'Bengali',
        'te': 'Telugu',
        'ta': 'Tamil',
        'ur': 'Urdu',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'ja': 'Japanese',
        'zh-cn': 'Chinese (Simplified)',
        'ar': 'Arabic'
    }

    # Map fonts for specific languages
    font_map = {
        'hi': "NotoSansDevanagari-Regular.ttf",
        'mr': "NotoSansDevanagari-Regular.ttf",
        'gu': "NotoSansGujarati-Regular.ttf",
        'bn': "NotoSansBengali-Regular.ttf",
        'te': "NotoSansTelugu-Regular.ttf",
        'ta': "NotoSansTamil-Regular.ttf",
        'ur': "NotoSansArabic-Regular.ttf",
        'kn': "NotoSansKannada-Regular.ttf",
        'ml': "NotoSansMalayalam-Regular.ttf",
        'pa': "NotoSansGurmukhi-Regular.ttf",
        'ja': "NotoSansJP-Regular.ttf",
        'zh-cn': "NotoSansSC-Regular.ttf",
        'ar': "NotoSansArabic-Regular.ttf"
    }

    translations = translate_transcript(transcript, languages)

    # Step 5: Save translations
    for lang_code, translation in translations.items():
        lang_name = languages[lang_code].lower()
        font_filename = font_map.get(lang_code, "NotoSans-Regular.ttf")
        font_path = os.path.join("fonts", font_filename)
        translation_file = os.path.join(output_dir, f"{base_filename}-{lang_name}.pdf")
        rtl = lang_code in ['ar', 'ur']  # Handle RTL languages
        save_to_pdf(translation_file, translation, font_name=f"Font_{lang_code}", font_path=font_path, rtl=rtl)

    # Step 6: Clean up the converted MP3 file
    if os.path.exists(mp3_file):
        os.remove(mp3_file)

import whisper
from pydub import AudioSegment
from pydub.utils import make_chunks
from googletrans import Translator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

def convert_mp4_to_mp3(mp4_path, mp3_path):
    """
    Convert an MP4 file to MP3 format.
    """
    print(f"Converting {mp4_path} to {mp3_path}...")
    audio = AudioSegment.from_file(mp4_path, format="mp4")
    audio.export(mp3_path, format="mp3")
    print("Conversion complete.")

def transcribe_long_audio(file_path, chunk_length_seconds=30):
    """
    Transcribe long audio files by splitting them into smaller chunks.
    """
    # Load the Whisper model
    model = whisper.load_model("base")

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
    for language in languages:
        print(f"Translating into {language}...")
        translation = translator.translate(transcript, dest=language).text
        translations[language] = translation
    return translations

def save_to_file(filename, content):
    """
    Save the given content to a text file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Saved to {filename}")

def txt_to_pdf(input_common_name, languages):
    """
    Convert text files into PDFs using appropriate fonts for each language.
    """
    fonts_folder = "fonts"

    # Language to font mapping
    language_fonts = {
        'hindi': "NotoSansDevanagari-Regular.ttf",
        'marathi': "NotoSansDevanagari-Regular.ttf",
        'gujarati': "NotoSansGujarati-Regular.ttf",
        'bengali': "NotoSansBengali-Regular.ttf",
        'telugu': "NotoSansTelugu-Regular.ttf",
        'tamil': "NotoSansTamil-Regular.ttf",
        'urdu': "NotoSansArabic-Regular.ttf",
        'kannada': "NotoSansKannada-Regular.ttf",
        'malayalam': "NotoSansMalayalam-Regular.ttf",
        'punjabi': "NotoSansGurmukhi-Regular.ttf",
        'spanish': "NotoSans-Regular.ttf",
        'french': "NotoSans-Regular.ttf",
        'german': "NotoSans-Regular.ttf",
        'italian': "NotoSans-Regular.ttf",
        'japanese': "NotoSansJP-Regular.ttf",
        'chinese (simplified)': "NotoSansSC-Regular.ttf",
        'arabic': "NotoSansArabic-Regular.ttf"
        # Add more language mappings as needed
    }

    for lang_code, lang_name in languages.items():
        txt_file_name = f"{input_common_name}-{lang_name.lower()}.txt"

        if not os.path.exists(txt_file_name):
            print(f"Skipping: {txt_file_name} not found.")
            continue

        font_file = language_fonts.get(lang_name.lower(), None)
        if not font_file:
            print(f"Skipping: No font defined for {lang_name}.")
            continue

        font_path = os.path.join(fonts_folder, font_file)
        if not os.path.exists(font_path):
            print(f"Skipping: Font file {font_file} not found in 'fonts' folder.")
            continue

        # Register the custom font
        font_name = f"CustomFont_{lang_name}"
        pdfmetrics.registerFont(TTFont(font_name, font_path))

        # Output PDF file path
        output_pdf_file = f"{input_common_name}-{lang_name.lower()}.pdf"

        # A4 page dimensions and margins
        page_width, page_height = A4
        margin = 50
        usable_width = page_width - 2 * margin
        font_size = 14
        line_spacing = font_size + 4

        # Initialize PDF canvas
        pdf = canvas.Canvas(output_pdf_file, pagesize=A4)
        pdf.setFont(font_name, font_size)

        # Read the input text
        with open(txt_file_name, "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()

        # Start writing text
        x_start = margin
        y_position = page_height - margin

        for line in lines:
            line = line.strip()
            if not line:
                continue

            while len(line) > 0:
                for i in range(len(line), 0, -1):
                    if pdf.stringWidth(line[:i], font_name, font_size) <= usable_width:
                        break

                pdf.drawString(x_start, y_position, line[:i].strip())
                line = line[i:].strip()

                y_position -= line_spacing

                if y_position < margin:
                    pdf.showPage()
                    pdf.setFont(font_name, font_size)
                    y_position = page_height - margin

        pdf.save()
        print(f"PDF created successfully: {output_pdf_file}")

if __name__ == "__main__":
    input_file = "small-eng.mp4"  # Replace with your MP4 file path
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    mp3_file = "converted_audio.mp3"

    # Step 1: Convert MP4 to MP3
    convert_mp4_to_mp3(input_file, mp3_file)

    # Step 2: Transcribe the MP3 file
    transcript = transcribe_long_audio(mp3_file, chunk_length_seconds=30)

    # Step 3: Save the English transcript
    eng_file = f"{base_filename}-eng.txt"
    save_to_file(eng_file, transcript)

    # Step 4: Translate the transcript into Hindi, Marathi, and Gujarati
    languages = {
        "hi": "Hindi",
        "mr": "Marathi",
        "gu": "Gujarati",
        "bn": "Bengali",
        "te": "Telugu",
        "ta": "Tamil",
        "ur": "Urdu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "ja": "Japanese",
        "zh-cn": "Chinese (Simplified)",
        "ar": "Arabic",
    }
    translations = translate_transcript(transcript, languages.keys())

    # Step 5: Save translations
    for lang_code, translation in translations.items():
        lang_name = languages[lang_code].lower()
        translation_file = f"{base_filename}-{lang_name}.txt"
        save_to_file(translation_file, translation)

    # Step 6: Generate PDFs
    txt_to_pdf(base_filename, languages)

    # Step 7: Clean up the converted MP3 file
    if os.path.exists(mp3_file):
        os.remove(mp3_file)

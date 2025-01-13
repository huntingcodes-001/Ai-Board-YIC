import whisper
from pydub import AudioSegment
from pydub.utils import make_chunks
from google.cloud import translate_v2 as translate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from pathlib import Path

# Directories
input_dir = r"C:\Users\CoE\Desktop\Final Smartboard\Ai-Board-YIC\1. whiteboard\src\recordings"  # Directory containing input files
output_dir = r"C:\Users\CoE\Desktop\Final Smartboard\Ai-Board-YIC\2. classroom\public\data\smartrec"  # Directory to check/create output folders

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
    model = whisper.load_model("base")
    audio = AudioSegment.from_file(file_path)
    chunk_length_ms = chunk_length_seconds * 1000
    chunks = make_chunks(audio, chunk_length_ms)

    chunk_dir = "audio_chunks"
    os.makedirs(chunk_dir, exist_ok=True)

    transcripts = []
    for i, chunk in enumerate(chunks):
        chunk_name = os.path.join(chunk_dir, f"chunk_{i}.mp3")
        chunk.export(chunk_name, format="mp3")
        print(f"Transcribing chunk {i+1}/{len(chunks)}: {chunk_name}")
        result = model.transcribe(chunk_name)
        transcripts.append(result["text"])

    full_transcript = " ".join(transcripts)
    for chunk_file in os.listdir(chunk_dir):
        os.remove(os.path.join(chunk_dir, chunk_file))
    os.rmdir(chunk_dir)

    return full_transcript

def translate_transcript(transcript, languages):
    """
    Translate the transcript into the specified languages using Google Cloud Translation API.
    """
    # Initialize the Google Cloud Translation API client
    client = translate.Client()

    translations = {}
    for language in languages:
        try:
            print(f"Translating into {language}...")
            result = client.translate(transcript, target_language=language)
            translations[language] = result['translatedText']
        except Exception as e:
            print(f"Error translating to {language}: {e}")
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
    Convert text files into PDFs using appropriate fonts for each language, including English.
    """
    fonts_folder = r"C:\Users\CoE\Desktop\Final Smartboard\Ai-Board-YIC\3. ml features\2. Video To Transcript with Trl\fonts"

    language_fonts = {
        'english': "NotoSans-Regular.ttf",
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
    }

    languages['en'] = 'English'

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

        font_name = f"CustomFont_{lang_name}"
        pdfmetrics.registerFont(TTFont(font_name, font_path))

        output_pdf_file = f"{input_common_name}-{lang_name.lower()}.pdf"

        page_width, page_height = A4
        margin = 50
        usable_width = page_width - 2 * margin
        font_size = 14
        line_spacing = font_size + 4

        pdf = canvas.Canvas(output_pdf_file, pagesize=A4)
        pdf.setFont(font_name, font_size)

        with open(txt_file_name, "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()

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

def create_output_folder(input_file, output_dir):
    """
    Create a folder to store all outputs based on the input file name in the output directory.
    """
    base_folder = Path(input_file).stem
    output_folder = Path(output_dir) / base_folder
    output_folder.mkdir(parents=True, exist_ok=True)
    return output_folder

if __name__ == "__main__":
    # Set the path to your Google Cloud API key file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\CoE\Desktop\Final Smartboard\Ai-Board-YIC\3. ml features\2. Video To Transcript with Trl\amir-translate.json"  # <-- Update this path

    # Process each file in the input directory
    for file_name in os.listdir(input_dir):
        input_file = os.path.join(input_dir, file_name)
        if not input_file.lower().endswith(".webm"):
            print(f"Skipping unsupported file: {file_name}")
            continue

        base_filename = os.path.splitext(os.path.basename(input_file))[0]
        output_folder = create_output_folder(input_file, output_dir)
        mp3_file = output_folder / "converted_audio.mp3"
        eng_file = output_folder / f"{base_filename}-english.txt"

        convert_webm_to_mp3(input_file, mp3_file)
        transcript = transcribe_long_audio(mp3_file, chunk_length_seconds=30)
        save_to_file(eng_file, transcript)

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

        for lang_code, translation in translations.items():
            lang_name = languages[lang_code].lower()
            translation_file = output_folder / f"{base_filename}-{lang_name}.txt"
            save_to_file(translation_file, translation)

        txt_to_pdf(output_folder / base_filename, languages)

        if mp3_file.exists():
            mp3_file.unlink()

        print(f"All outputs for {file_name} saved in folder: {output_folder}")

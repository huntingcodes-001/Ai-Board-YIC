import whisper
from pydub import AudioSegment
from pydub.utils import make_chunks
from googletrans import Translator
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

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

def txt_to_pdf(input_txt_file, output_pdf_file, font_file, font_size=14):
    """
    Convert a .txt file to a .pdf file with custom font support.
    """
    try:
        # Register the custom font
        pdfmetrics.registerFont(TTFont("CustomFont", font_file))

        # A4 page dimensions and margins
        page_width, page_height = A4
        margin = 50  # 50 points margin (~0.7 inches)
        usable_width = page_width - 2 * margin
        line_spacing = font_size + 4  # Spacing between lines

        # Initialize PDF canvas
        pdf = canvas.Canvas(output_pdf_file, pagesize=A4)
        pdf.setFont("CustomFont", font_size)

        # Read the input text
        with open(input_txt_file, "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()

        # Start writing text
        x_start = margin
        y_position = page_height - margin

        for line in lines:
            line = line.strip()  # Clean up unnecessary whitespace
            if not line:
                continue  # Skip empty lines

            # Split long lines to fit within the usable width
            while len(line) > 0:
                # Find the maximum number of characters that fit in the usable width
                for i in range(len(line), 0, -1):
                    if pdf.stringWidth(line[:i], "CustomFont", font_size) <= usable_width:
                        break
                
                # Draw the part of the line that fits
                pdf.drawString(x_start, y_position, line[:i].strip())
                line = line[i:].strip()  # Remove the written part

                # Move to the next line
                y_position -= line_spacing

                # Add a new page if the current page is full
                if y_position < margin:
                    pdf.showPage()
                    pdf.setFont("CustomFont", font_size)
                    y_position = page_height - margin

        # Save the PDF
        pdf.save()
        print(f"PDF created successfully: {output_pdf_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to run
if __name__ == "__main__":
    input_file = "small-eng.mp4"  # Replace with your MP4 file path
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.getcwd(), base_filename)
    os.makedirs(output_dir, exist_ok=True)

    mp3_file = os.path.join(output_dir, "converted_audio.mp3")

    # Step 1: Convert MP4 to MP3
    convert_mp4_to_mp3(input_file, mp3_file)

    # Step 2: Transcribe the MP3 file
    transcript = transcribe_long_audio(mp3_file, chunk_length_seconds=30)

    # Step 3: Save the English transcript
    eng_file = os.path.join(output_dir, f"{base_filename}-eng.txt")
    with open(eng_file, "w", encoding="utf-8") as file:
        file.write(transcript)

    # Step 4: Translate the transcript into multiple languages
    languages = {
        'gu': 'Gujarati',
        'bn': 'Bengali',
        'te': 'Telugu',
        'ta': 'Tamil',
        'ur': 'Urdu',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'ar': 'Arabic',
        'zh-cn': 'Chinese (Simplified)',
        'ja': 'Japanese'
    }

    # Map fonts for specific languages
    font_map = {
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
        translation_file = os.path.join(output_dir, f"{base_filename}-{lang_name}.txt")
        pdf_file = os.path.join(output_dir, f"{base_filename}-{lang_name}.pdf")
        with open(translation_file, "w", encoding="utf-8") as file:
            file.write(translation)
        font_path = font_map.get(lang_code, "NotoSans-Regular.ttf")  # Default font
        txt_to_pdf(translation_file, pdf_file, font_path)
    
    # Step 6: Clean up the converted MP3 file
    if os.path.exists(mp3_file):
        os.remove(mp3_file)

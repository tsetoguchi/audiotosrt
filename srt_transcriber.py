from typing import List

import whisper
import re
import string
from tqdm import tqdm
import srt_text_comparer

# Update these settings
LANGUAGE = "en"
MODEL_SIZE = "medium"
LYRICS = "lonely.txt"
AUDIO = "lonely.mp3"
OUTPUT_NAME = f"{AUDIO[:-4].title()} SRT"


def sanitize_text(text: str) -> str:
    """Sanitizes text for better matching."""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_lyrics(lyrics_file: str) -> List[str]:
    """Loads and cleans a lyrics file."""
    with open(lyrics_file, "r", encoding="utf-8") as f:
        lyrics = f.readlines()

    # Process lyrics
    cleaned_lyrics = []
    for line in lyrics:
        line = line.strip()
        if line:
            cleaned_lyrics.append(line)

    print(f"Loaded {len(cleaned_lyrics)} lines from lyrics file")
    return cleaned_lyrics



def transcribe_to_srt(audio_file: str, lyrics_file: str, output_srt: str, language: str):
    """Transcribes an audio file and generates an SRT file."""
    print("Loading model...")
    model = whisper.load_model(MODEL_SIZE)
    print("Transcribing audio...")

    # Use specified language setting
    result = model.transcribe(audio_file, language=language)

    # Load lyrics (we'll use them for line-by-line alignment)
    lyrics = load_lyrics(lyrics_file)
    lyrics_index = 0

    # Generate SRT file directly from transcription
    with open(output_srt, "w", encoding="utf-8") as f:
        for i, segment in enumerate(tqdm(result["segments"], desc="Generating SRT", unit="segment"), start=1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()

            # If we have lyrics available and haven't used them all
            if lyrics_index < len(lyrics):
                # Use the next lyric from the file
                output_text = lyrics[lyrics_index]
                lyrics_index += 1
            else:
                # If we've used all lyrics, use the transcribed text
                output_text = text

            f.write(f"{i}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{output_text}\n\n")

    print(f"\n✅ SRT file saved: {output_srt}")
    print(f"Used {min(lyrics_index, len(lyrics))} lyrics lines")



def format_time(seconds: float) -> str:
    """Converts seconds to SRT time format (hh:mm:ss,ms)."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = (int(seconds) // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# Example Usage
if __name__ == "__main__":
    transcribe_to_srt(f"audio/{AUDIO}", f"lyrics/{LYRICS}", f"SRT/{OUTPUT_NAME}", LANGUAGE)
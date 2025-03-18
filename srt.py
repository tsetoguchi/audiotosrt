import whisper
import re
from difflib import get_close_matches


def load_lyrics(lyrics_file):
    """Loads and cleans a lyrics file."""
    with open(lyrics_file, "r", encoding="utf-8") as f:
        lyrics = f.readlines()
    return [line.strip() for line in lyrics if line.strip()]


def find_best_match(transcribed_text, lyrics):
    """Finds the closest match in lyrics for a transcribed segment."""
    match = get_close_matches(transcribed_text, lyrics, n=1, cutoff=0.5)
    return match[0] if match else transcribed_text


def transcribe_audio(audio_file, lyrics_file, output_srt):
    """Transcribes an audio file and generates an SRT file using lyrics as a reference."""
    model = whisper.load_model("medium")  # You can use "small", "base", etc.
    result = model.transcribe(audio_file)
    lyrics = load_lyrics(lyrics_file)

    with open(output_srt, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], start=1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            matched_text = find_best_match(text, lyrics)

            f.write(f"{i}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{matched_text}\n\n")

    print(f"SRT file saved: {output_srt}")


def format_time(seconds):
    """Converts seconds to SRT time format (hh:mm:ss,ms)."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = (int(seconds) // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# Example Usage
if __name__ == "__main__":
    transcribe_audio("audio/narita.wav", "lyrics/narita.txt", "output.srt")

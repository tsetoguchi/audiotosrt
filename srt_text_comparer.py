from typing import List
import re

"""Compares the given SRT and TEXT files
True if equal otherwise False"""

SRT = ""
TEXT = ""

def srt_text_is_equal(srt_file_name: str, text_file_name: str) -> bool:
    with open(f"SRT/{srt_file_name}", "r", encoding="utf-8") as f:
        srt = f.readlines()
    sanitized_srt = sanitize_srt(srt)

    with open(f"lyrics/{text_file_name}.txt", "r", encoding="utf-8") as f:
        text = f.readlines()
    sanitized_text = sanitize_text(text)

    i = 0

    # In the case of one of the files being shorter than the other, due to one containing repetition, it will only
    # check for equality for the length of the shorter file
    while i < min(len(sanitized_text), len(sanitized_srt)):
        if sanitized_text[i] != sanitized_srt[i]:
            return False
        i += 1

    return True

"""Sanitizes text file"""
def sanitize_text(text: List[str]) -> List[str]:
    sanitized = []

    for line in text:
        line = line.strip()

        if line:
            sanitized.append(line)


    return sanitized

"""Sanitizes SRT file"""
def sanitize_srt(srt: List[str]) -> List[str]:

    sanitized = []
    for line in srt:
        if not line.strip() or re.match(r"^\d+$", line) or re.match(r"^\d{2}:\d{2}:\d{2},\d{3} -->", line):
            continue
        line = line.strip()
        sanitized.append(line)



    return sanitized



if __name__ == "__main__":
    print(f"Chocolate Disco: {srt_text_is_equal('chocolate disco SRT', 'chocolate disco')}")
    print(f"Hold On: {srt_text_is_equal('Hold On.mp3 SRT', 'Hold On')}")
    print(f"Lonely: {srt_text_is_equal('Lonely SRT', 'lonely')}")


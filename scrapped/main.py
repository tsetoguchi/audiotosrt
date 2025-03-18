import whisperx


#  clear GPU memory
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"cuDNN version: {torch.backends.cudnn.version()}")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {torch.cuda.get_device_name(0)}")
print(torch.cuda.is_available())  # Should be True
print(torch.version.cuda)         # Should show 12.1
print(torch.cuda.get_device_name(0))  # Should print your GPU name



# Path to audio file and model setup
audio_file = "../audio/lonely.mp3"

compute_type = "float32"

# Load model
model = whisperx.load_model("medium", device, compute_type=compute_type)


# Transcribe audio
result = model.transcribe(audio_file)

# Align using forced alignment (if you have the lyrics)


with open("../lyrics/lonely.txt", "r", encoding="utf-8") as f:
    lyrics = f.read()

aligned_result = whisperx.align(result["segments"], lyrics, device)

print("right before save")

# Save to SRT file
with open("../output.srt", "w", encoding="utf-8") as f:
    for i, segment in enumerate(aligned_result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        f.write(f"{i + 1}\n")
        f.write(f"{start:.3f} --> {end:.3f}\n")
        f.write(f"{text}\n\n")

print("SRT file generated: output.srt")

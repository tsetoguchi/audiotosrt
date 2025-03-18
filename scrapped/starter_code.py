# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 22:01:17 2025
@author: tao
Modified to include lyrics-based transcription enhancement
"""
import whisperx
import gc
import torch
import os
import difflib
from typing import List, Dict, Any

def load_lyrics_file(file_path: str) -> str:
    """Load lyrics from a text file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Lyrics file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lyrics = f.read()
    
    return lyrics

def enhance_transcription_with_lyrics(segments: List[Dict[Any, Any]], lyrics: str) -> List[Dict[Any, Any]]:
    """Enhance transcription segments using provided lyrics as reference."""
    # Combine all transcribed text
    transcribed_text = ' '.join([segment['text'] for segment in segments])
    
    # Use difflib to find best alignment between transcription and lyrics
    # This helps when whisper got parts wrong but overall structure is similar
    matcher = difflib.SequenceMatcher(None, transcribed_text.lower(), lyrics.lower())
    
    # Create a mapping of matched sections
    matches = matcher.get_matching_blocks()
    
    # Keep track of where we are in the segments
    current_position = 0
    enhanced_segments = []
    
    # For each segment, check if it can be improved with lyrics
    for segment in segments:
        segment_length = len(segment['text'])
        segment_start = current_position
        segment_end = segment_start + segment_length
        
        # Find the best match in lyrics for this segment
        best_match = None
        highest_ratio = 0.7  # Threshold for replacement
        
        # Check each difflib match
        for match in matches:
            a, b, size = match  # a is position in transcribed_text, b is position in lyrics
            
            # If this match overlaps with our current segment
            if not (a + size <= segment_start or a >= segment_end):
                # Calculate how much of the segment is covered by this match
                overlap_start = max(a, segment_start)
                overlap_end = min(a + size, segment_end)
                overlap_size = overlap_end - overlap_start
                
                segment_coverage = overlap_size / segment_length
                
                if segment_coverage > highest_ratio:
                    highest_ratio = segment_coverage
                    
                    # Extract corresponding part from lyrics
                    lyrics_start = b + (overlap_start - a)
                    lyrics_end = lyrics_start + overlap_size
                    best_match = lyrics[lyrics_start:lyrics_end]
        
        # Create enhanced segment
        enhanced_segment = segment.copy()
        if best_match:
            enhanced_segment['text'] = best_match
            enhanced_segment['enhanced'] = True
        else:
            enhanced_segment['enhanced'] = False
            
        enhanced_segments.append(enhanced_segment)
        current_position += segment_length + 1  # +1 for the space we added between segments
    
    return enhanced_segments

def transcribe_with_lyrics_assistance(audio_file: str, lyrics_file: str = None, batch_size: int = 16, 
                                      compute_type: str = "float16", device: str = "cuda",
                                      model_name: str = "large-v2") -> Dict[str, Any]:
    """
    Transcribe audio using WhisperX with lyrics assistance for improved accuracy.
    
    Args:
        audio_file: Path to the audio file
        lyrics_file: Path to the lyrics text file (optional)
        batch_size: Batch size for processing
        compute_type: Computation type (float16/int8)
        device: Device to run on (cuda/cpu)
        model_name: Whisper model to use
        
    Returns:
        Dictionary containing transcription results with segments
    """
    # 1. Load and prepare model
    model = whisperx.load_model(model_name, device, compute_type=compute_type)
    audio = whisperx.load_audio(audio_file)
    
    # 2. Initial transcription with whisper
    result = model.transcribe(audio, batch_size=batch_size)
    print("Initial transcription complete.")
    
    # 3. Align whisper output
    language_code = result["language"]
    model_a, metadata = whisperx.load_align_model(language_code=language_code, device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    print("Alignment complete.")
    
    # Clean up alignement model to save memory
    del model_a
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    
    # 4. If lyrics file provided, enhance the transcription
    if lyrics_file:
        try:
            lyrics = load_lyrics_file(lyrics_file)
            original_segments = result["segments"].copy()
            enhanced_segments = enhance_transcription_with_lyrics(result["segments"], lyrics)
            result["segments"] = enhanced_segments
            result["original_segments"] = original_segments
            print("Lyrics enhancement applied.")
        except Exception as e:
            print(f"Error applying lyrics enhancement: {e}")
    
    return result

if __name__ == "__main__":
    # Configuration
    device = "cuda"  # Use "cpu" if no GPU available
    audio_file = "../audio/lonely.mp3"
    lyrics_file = "../lyrics/lonely.txt"  # Path to lyrics file
    batch_size = 16  # Reduce if low on GPU memory
    compute_type = "float16"  # Change to "int8" if low on GPU memory
    
    # Run transcription with lyrics assistance
    result = transcribe_with_lyrics_assistance(
        audio_file=audio_file,
        lyrics_file=lyrics_file,
        batch_size=batch_size,
        compute_type=compute_type,
        device=device
    )
    
    # Print results
    print("\nTranscription Results:")
    print("-" * 50)
    
    for i, segment in enumerate(result["segments"]):
        enhanced = segment.get('enhanced', False)
        print(f"[{segment['start']:.2f} → {segment['end']:.2f}] {'✓ ' if enhanced else ''}  {segment['text']}")
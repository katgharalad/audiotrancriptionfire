from llama_cpp import Llama
import json
from typing import List, Dict
import re
from datetime import datetime

class EmergencyProcessor:
    def __init__(self, model_path: str = "models/llama-2-7b.Q4_K_M.gguf"):
        """Initialize the emergency processor with LLaMA model."""
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=6   # Number of CPU threads to use
        )
        
        # System prompt for emergency dispatch processing
        self.system_prompt = """You are an AI emergency dispatch assistant. Your task is to:
1. Clean up transcription errors
2. Structure conversations into clear emergency reports
3. Extract key information
4. Format output as a structured dispatch report

Focus on these key elements:
- Location details
- Caller identity/status
- Incident type/severity
- Immediate risks
- Required response

Be factual and precise. Do not invent details."""

    def clean_transcript(self, transcript: List[Dict[str, str]]) -> str:
        """Clean and format the transcript for processing."""
        cleaned_lines = []
        for entry in transcript:
            # Extract timestamp and text
            timestamp = entry.get('timestamp', '')
            speaker = entry.get('speaker', '')
            text = entry.get('text', '').strip()
            
            # Remove duplicate phrases
            text = re.sub(r'(\b\w+\b)( \1\b)+', r'\1', text)
            
            # Format the line
            cleaned_lines.append(f"[{timestamp}] {speaker}: {text}")
        
        return "\n".join(cleaned_lines)

    def process_transcript(self, transcript: List[Dict[str, str]]) -> str:
        """Process the transcript and generate an emergency report."""
        # Clean the transcript
        cleaned_transcript = self.clean_transcript(transcript)
        
        # Construct the prompt
        prompt = f"{self.system_prompt}\n\nTranscript:\n{cleaned_transcript}\n\nGenerate a structured emergency dispatch report:"
        
        # Generate response using LLaMA
        response = self.llm(
        prompt,
        max_tokens=1024,  # Increased token limit to prevent truncation
        temperature=0.1,  
        stop=["</report>", "\n\n\n", "END OF REPORT"]  # More robust stopping
    )
        
        return response['choices'][0]['text']

    def update_report(self, current_report: str, new_transcript: List[Dict[str, str]]) -> str:
        """Update existing report with new transcript information."""
        # Combine current report with new transcript
        prompt = f"{self.system_prompt}\n\nCurrent Report:\n{current_report}\n\nNew Transcript:\n{self.clean_transcript(new_transcript)}\n\nUpdate the emergency dispatch report:"
        
        response = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.1,
            stop=["</report>", "\n\n\n"]
        )
        
        return response['choices'][0]['text']

def format_transcript_entry(timestamp: datetime, speaker: str, text: str) -> Dict[str, str]:
    """Format a transcript entry for processing."""
    return {
        'timestamp': timestamp.strftime('%H:%M:%S'),
        'speaker': speaker,
        'text': text
    } 
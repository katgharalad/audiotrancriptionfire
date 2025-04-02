# AudioTranscripY + ML Interpretation Layer Integration

This directory contains scripts for integrating the AudioTranscripY transcription system with the ML interpretation layer for emergency incident processing.

## Overview

The integration connects two main components:
1. **AudioTranscripY**: Records audio and transcribes it using Whisper
2. **ML Interpretation Layer**: Analyzes transcripts to extract emergency incident information

## Key Components

### `run_integration.py`
This script orchestrates the end-to-end process:
- Activates the AudioTranscripY environment and runs its transcription
- Processes the resulting transcript using the whole conversation processor
- Displays a summary of the interpretation and routing results

### `whole_conversation_processor.py`
This processor handles the analysis of complete transcripts:
- Processes the entire conversation context rather than individual speaker lines
- Extracts emergency incident information (type, location, casualties)
- Applies the ML interpretation layer for enhanced features
- Routes the incident to the appropriate dispatcher
- Saves comprehensive interpretation results

## How It Works Without Speaker Diarization

While AudioTranscripY attempts to identify speakers with labels like "Speaker 1" and "Speaker 2", this information is often unreliable. Our interpretation system is designed to process the entire conversation as a whole:

1. **Text Extraction**: The processor extracts the full conversation text, ignoring speaker labels
2. **Pattern Recognition**: It identifies key information using regex patterns and keyword matching:
   - Incident types (fire, gas leak, etc.)
   - Addresses (street numbers and names)
   - Casualties (counts, trapped individuals)
   - Special circumstances (children, elderly, pets)
3. **Context Understanding**: The system analyzes the complete context to determine the nature of the emergency
4. **Enhanced Processing**: The ML layer adds confidence scores, validates addresses, predicts priority, and structures casualty information

This approach has several advantages:
- Works even when speaker diarization is inaccurate or missing
- Captures information from both caller and dispatcher
- Handles interruptions and conversational flow
- Maintains context throughout the entire emergency call

## Running the Integration

To run the complete integration:
```
python integration/run_integration.py
```

This will:
1. Start AudioTranscripY for real-time audio capture and transcription
2. Process the transcript using the whole conversation processor
3. Generate structured incident information and routing decisions
4. Save the results to JSON files in the `interpretation_outputs` directory 
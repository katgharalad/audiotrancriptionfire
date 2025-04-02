# Integrating AudioTranscripY with ML Interpretation Layer

This guide explains how to connect the AudioTranscripY real-time transcription system with the ML interpretation layer for emergency call classification and routing.

## Integration Options

### Option 1: Using the integration.py script

For a seamless integration experience, you can use the provided integration script:

1. Ensure both repositories are properly set up:
   ```bash
   # Clone repositories if needed
   git clone https://github.com/katgharalad/audiotrancriptionfire.git
   
   # Make sure dependencies are installed
   pip install -r requirements.txt
   pip install -r ml_interpretation/requirements.txt
   ```

2. Run the integration script:
   ```bash
   python ml_interpretation/integration.py
   ```

3. The integration script will:
   - Create a modified version of AudioTranscripY's main.py
   - Connect the transcript output to the ML interpretation layer
   - Process Speaker 2 (caller) transcripts in real-time
   - Generate structured incident data with confidence scores, validation, and priority

### Option 2: Manual Integration (Recommended)

For more control over the integration process, you can manually integrate the systems:

1. Add the following code to your main.py file after processing a transcript:

   ```python
   # Import ML interpretation components
   from ml_interpretation.main import AudioTranscriptInterpreter
   from ml_interpretation.dispatcher_router import IncidentRouter
   
   # Initialize once
   interpreter = AudioTranscriptInterpreter()
   router = IncidentRouter()
   
   # In your transcript processing function, after a new transcript is identified:
   if speaker == "Speaker 2":  # Speaker 2 is the caller
       # Process with ML interpreter
       result = interpreter.process_transcript(transcript)
       
       # Route the incident
       routing_result = router.route(result)
       
       # Print or use the structured interpretation
       print("\nEMERGENCY CALL INTERPRETATION")
       print("="*50)
       print(f"INCIDENT TYPE: {result['incident_type'].upper()}")
       print(f"LOCATION: {result['address']}")
       print(f"CASUALTIES: {result['casualties']}")
       print(f"PRIORITY: {routing_result['interpretation']['priority_level']} ({routing_result['interpretation']['priority']})")
       print("="*50)
   ```

2. This will ensure that any time Speaker 2 (the caller) speaks, their transcription will be processed through the ML interpretation layer.

## Running the Integrated System

1. Start AudioTranscripY with the ML integration:
   ```bash
   python main.py  # If using the manual integration approach
   ```

2. When you speak into the microphone:
   - AudioTranscripY will transcribe the speech in real-time
   - Speaker 2 transcripts will be processed by the ML interpretation layer
   - Incident classifications will be displayed with confidence scores
   - Address, casualties, and priority information will be structured
   - Low-confidence predictions will be flagged for verification

3. Press Enter at any time to stop recording.

## Expected Output

When a caller (Speaker 2) transcript is processed, you'll see output like this:

```
EMERGENCY CALL INTERPRETATION
==================================================
INCIDENT TYPE: STRUCTURE FIRE
CONFIDENCE: 0.94
LOCATION: 456 elm road
ADDRESS VALID: True (Confidence: 0.22)
CASUALTIES: caller trapped
AFFECTED: Caller
PRIORITY: CRITICAL (4.8)
STATUS: REQUIRES VERIFICATION
==================================================
```

## Troubleshooting

- If you encounter import errors, ensure the ml_interpretation directory is in your Python path.
- Audio dependency issues may occur depending on your system. In that case, prefer the manual integration approach.
- For best results, use a high-quality microphone in a quiet environment.

For further assistance, please refer to the detailed documentation in the ml_interpretation/README.md file. 
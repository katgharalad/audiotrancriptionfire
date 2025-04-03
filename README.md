# AudioTranscripY + Delaware County Validation Engine Integration

A comprehensive emergency call processing system that integrates real-time audio transcription, address validation, and machine learning interpretation to generate structured dispatch reports.

## System Components

### 1. Audio Transcription Layer
- Records and processes audio from microphone input
- Transcribes speech using OpenAI's Whisper model
- Supports both real-time and file-based transcription
- Identifies speaker turns in conversations

### 2. Address Validation Engine
- Validates addresses against Delaware County's GIS database
- Reverse geocodes partial addresses and landmarks
- Provides confidence scores for address matching
- Flags addresses that need verification
- Enriches addresses with jurisdiction and zip code data

### 3. ML Interpretation Layer
- Classifies incident types (structure fire, vehicle accident, etc.)
- Extracts casualty information
- Determines incident priority
- Generates structured dispatch reports

## Getting Started

### Prerequisites
- Python 3.9+
- A working microphone for audio recording
- Approximately 2GB of RAM for models and processing

### Installation

1. Clone this repository:
```
git clone https://github.com/katgharalad/audiotrancriptionfire.git
cd audiotrancriptionfire
```

2. Create a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Install Whisper for audio transcription:
```
pip install git+https://github.com/openai/whisper.git
```

### Usage

#### Running the Integrated System

```
python run_integrated_system.py
```

This script orchestrates the complete workflow:
1. Records or simulates audio input
2. Transcribes the audio using Whisper
3. Validates addresses using the validation engine
4. Processes the transcript through the ML interpretation layer
5. Generates a dispatch report

#### Testing with Simulated Audio

```
python audio_simulation_transcription.py --simulate
```

This allows you to type a transcript instead of recording audio, which is useful for testing.

#### Processing Pre-recorded Audio

```
python audio_simulation_transcription.py --audio path/to/audio.wav
```

#### Processing Existing Transcripts

```
python audio_simulation_transcription.py --transcript path/to/transcript.txt
```

#### Testing Without Address Validation

```
python audio_simulation_transcription.py --simulate --skip-validation
```

## System Architecture

```
┌─────────────────┐     ┌───────────────────┐     ┌─────────────────┐
│  Audio Input    │────▶│  Transcription    │────▶│ Address         │
│  (Microphone/   │     │  (Whisper)        │     │ Validation      │
│   File/Text)    │     │                   │     │ Engine          │
└─────────────────┘     └───────────────────┘     └────────┬────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌───────────────────┐     ┌─────────────────┐
│  Dispatch       │◀────│  Report           │◀────│ ML              │
│  Interface      │     │  Generation       │     │ Interpretation  │
│                 │     │                   │     │ Layer           │
└─────────────────┘     └───────────────────┘     └─────────────────┘
```

## Validation Engine Details

The Delaware County Address Validation Engine provides:

- **Address Point Validation**: Matches addresses against Delaware County's address points database
- **Street Centerline Validation**: Validates street names and numbering
- **Landmark Recognition**: Identifies schools, parks, government buildings, etc.
- **Jurisdiction Assignment**: Determines which municipality/township has jurisdiction
- **ZIP Code Validation**: Validates and assigns ZIP codes to addresses
- **Confidence Scoring**: Provides match confidence from 0.0 to 1.0

## ML Interpretation Details

The ML Interpretation Layer processes transcripts to:

- **Classify Incident Types**:
  - Structure fires (various types)
  - Vehicle accidents
  - Medical emergencies
  - Gas leaks
  - And more...

- **Extract Casualty Information**:
  - Number of people involved
  - Special categories (children, elderly, pets)
  - Entrapment situations

- **Determine Priority Levels**:
  - Critical (5.0): Immediate life-threatening situations
  - Urgent (4.0-4.9): Serious emergencies requiring fast response
  - High (3.0-3.9): Significant emergencies 
  - Medium (2.0-2.9): Non-life-threatening situations
  - Low (1.0-1.9): Minor incidents

## Output Format

The system generates a structured JSON dispatch report:

```json
{
  "transcript": "Speaker 2: There's a fire at 123 Main Street with two people trapped inside!",
  "timestamp": "2024-09-11T14:32:45.123456",
  "address": "123 Main Street",
  "landmark": null,
  "zip_code": "43015",
  "jurisdiction": "City of Delaware",
  "incident_type": "structure_fire",
  "priority": 4.5,
  "needs_verification": false
}
```

## File Structure

```
audiotranscriptionfire/
├── audio_simulation_transcription.py  # Main script for audio simulation
├── process_audio_file.py              # Process pre-recorded audio files
├── run_integrated_system.py           # Complete workflow orchestration
├── test_transcript.txt                # Sample test transcript
├── sample_emergency_transcript.txt    # Sample emergency transcript
├── README.md                          # This file
├── VALIDATION_INTEGRATION.md          # Validation integration details
├── PROJECT_INVENTORY.md               # Comprehensive file inventory
├── validationengine/                  # Address validation engine
│   ├── __init__.py
│   ├── validation_engine.py           # Original validation engine
│   ├── validation_engine_v2.py        # Enhanced validation engine
│   ├── setup_venv.py                  # Setup virtual environment
│   ├── version_check.py               # Version compatibility check
│   └── [CSV data files]               # GIS data for address validation
└── ml_interpretation/                 # ML interpretation layer
    ├── interpreter.py                 # Core ML interpretation logic
    ├── model_training.py              # Model training utilities
    └── integrated_demo.py             # Demo script for testing
```

## Limitations

- Speaker identification works best with distinct voices
- Background noise can affect transcription quality
- Address validation is specific to Delaware County
- Very quiet speech might not be detected
- Accuracy depends on clear enunciation and audio quality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Created by katgharalad
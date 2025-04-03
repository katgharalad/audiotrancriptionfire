# AudioTranscripY + Validation Engine Integration

This document describes how the Delaware County Address Validation Engine has been integrated with the AudioTranscripY ML Interpretation layer.

## Integration Overview

The integration enhances the AudioTranscripY system by adding advanced address validation, landmark recognition, and jurisdiction determination capabilities to emergency call transcripts.

### Key Features Added

- Address validation against Delaware County GIS data
- Landmark-to-address resolution (e.g., "Smith Elementary" → "450 North Liberty Street")
- Jurisdiction assignment (city, township)
- ZIP code validation and matching
- Confidence scoring for address information
- Relative location interpretation ("across from", "behind", etc.)

## Implementation Details

### File Structure

```
ml_interpretation/
├── interpreter.py             # NEW: Main integration point with validation engine
├── test_validation_integration.py  # NEW: Test script for the integration
├── requirements.txt           # UPDATED: Added validation engine dependencies
├── README.md                  # Existing documentation
└── whole_conversation_processor.py  # Existing processor file

validationengine/
├── validation_engine_v2.py    # Main validation engine code
├── __init__.py                # Module import definitions
├── setup_venv.py              # NEW: Virtual environment setup script
├── run_validation.py          # NEW: Script to run validation directly
├── version_check.py           # NEW: Version compatibility check
├── requirements.txt           # Dependencies for validation engine
└── venv/                      # Virtual environment (created by setup_venv.py)
```

### Integration Points

The Validation Engine is integrated at these points:

1. **Initialization**: The AudioTranscriptInterpreter class now initializes the AddressValidationEngine
2. **Transcript Processing**: The process_transcript() method calls generate_validation_report()
3. **Result Enrichment**: Validation results are merged into the ML interpretation output
4. **Verification Flagging**: Address confidence is used in determining overall verification needs

## Virtual Environment Setup

The validation engine is designed to run in its own virtual environment to avoid dependency conflicts. Two approaches are supported:

### 1. Integrated Mode (Recommended)

In this mode, the validation engine is imported directly into the AudioTranscriptInterpreter.

```python
from ml_interpretation.interpreter import AudioTranscriptInterpreter

# Initialize with validation data directory
interpreter = AudioTranscriptInterpreter(
    validation_data_dir="/path/to/validationengine"
)
```

### 2. Standalone Mode

In this mode, the validation engine runs in its own virtual environment as a separate process.

```
# Set up the virtual environment
cd validationengine
python setup_venv.py

# Run validation directly
python run_validation.py "Speaker 2: There's a fire at Smith Elementary."
```

## Version Compatibility

The validation engine exists in two versions:
- `validation_engine.py` (original version)
- `validation_engine_v2.py` (enhanced version with more features)

The integration uses `validation_engine_v2.py` by default. To check for version compatibility and clean up redundant files:

```
python validationengine/version_check.py
```

This script will:
1. Check which versions exist
2. Ensure __init__.py imports the correct version
3. Optionally backup and remove redundant versions

## Using the Integration

### Basic Usage

```python
from ml_interpretation.interpreter import AudioTranscriptInterpreter

# Initialize the interpreter with validation engine
interpreter = AudioTranscriptInterpreter()

# Process a transcript
transcript = "Speaker 2: There's a fire in front of Smith Elementary."
result = interpreter.process_transcript(transcript)

# Access validation results
address = result.get("reverse_geocoded_address")  # "450 North Liberty Street"
landmark = result.get("landmark")  # "Smith Elementary"
zip_code = result.get("matched_zip")  # "43015"
jurisdiction = result.get("jurisdiction")  # "City of Delaware"
confidence = result.get("address_confidence")  # 0.88
needs_verification = result.get("needs_verification")  # False
```

### Testing the Integration

You can test the integration using:

1. **Test Script**: Run the test validation integration script:
   ```
   cd ml_interpretation
   python test_validation_integration.py
   ```

2. **Integrated Demo**: Run the integrated demo with validation test mode:
   ```
   python integrated_demo.py --mode validation_test
   ```

3. **Direct Validation**: Test the validation engine directly:
   ```
   python validationengine/run_validation.py
   ```

## Error Handling

The integration includes robust error handling:

1. **Import Errors**: Falls back to basic processing if validation engine is unavailable
2. **Initialization Errors**: Logs errors and continues without validation
3. **Processing Errors**: Catches exceptions during validation to prevent crashes

## Output Format

The integrated output format includes:

```json
{
  "incident_type": "structure fire",
  "casualties": "none",
  "priority": 3.5,
  "priority_level": "HIGH",
  "reverse_geocoded_address": "450 North Liberty Street",
  "landmark": "Smith Elementary",
  "address_confidence": 0.88,
  "matched_zip": "43015",
  "jurisdiction": "City of Delaware",
  "needs_verification": false,
  "timestamp": "2023-04-02T22:30:45.123456",
  "transcript": "Speaker 2: There's a fire in front of Smith Elementary."
}
```

## Dependencies

The integration requires these additional dependencies:
- fuzzywuzzy>=0.18.0
- python-Levenshtein>=0.12.0
- pathlib>=1.0.1

These have been added to the ml_interpretation/requirements.txt file. 
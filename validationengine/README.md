# AudioTranscripY – Landmark-Aware Address Validation Engine

A validation engine for Delaware, OH that uses official county GIS datasets to validate and enrich addresses extracted from emergency transcripts. Enables semantic landmark-to-address inference for more accurate dispatching.

## Purpose

This tool helps emergency services accurately validate and match addresses mentioned in emergency call transcripts, even when the caller uses landmarks instead of specific addresses.

## Features

- Validates caller-provided addresses against Delaware County certified data
- Reverse-resolves landmarks (schools, churches, stores) to their closest known addresses
- Calculates address confidence and jurisdiction alignment
- Provides structured address output with confidence scores

## Data Inputs

The engine uses the following official Delaware County GIS datasets:
- Address Points (`Address_Point_6449015960905250632 (1).csv`)
- Street Centerlines (`Street_Centerline_7861883908334951619.csv`)
- MSAG Boundaries (`MSAG_155522220392559522.csv`)
- Parcel Data (`Parcel_188782905266197535.csv`)
- Zip Code Boundaries (`Zip_Code_-4600858990630826378.csv`)

## Setup

### Standard Setup
1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Ensure all CSV data files are in the project directory

### Virtual Environment Setup (Recommended)
For better isolation and dependency management, use the included setup script:

```bash
# Set up a virtual environment with all dependencies
python setup_venv.py

# Run the validation engine in its own environment
python run_validation.py
```

### Integration Setup
To integrate with AudioTranscripY ML interpretation layer:

```bash
# Run the full integration setup script
python setup_validation_integration.py
```

## Version Information
The validation engine has two versions:
- `validation_engine.py` - Original version
- `validation_engine_v2.py` - Enhanced version with improved landmark detection and relative location understanding

You can check and manage versions using:
```bash
python version_check.py
```

## Usage

### Direct Usage
```python
from validation_engine_v2 import AddressValidationEngine

# Initialize the engine
engine = AddressValidationEngine()

# Validate a transcript
transcript = "There's a fire in front of Smith Elementary and kids are stuck inside."
result = engine.generate_validation_report(transcript)

# Print the result
print(result)
```

### Via Run Script
```bash
python run_validation.py "Speaker 2: There's a fire at Smith Elementary School."
```

### Via Integration
```python
from ml_interpretation.interpreter import AudioTranscriptInterpreter

# Initialize the integrated interpreter
interpreter = AudioTranscriptInterpreter()

# Process a transcript
result = interpreter.process_transcript("Speaker 2: There's a fire at Smith Elementary.")
print(result)
```

## Output Example

```json
{
  "landmark": "Smith Elementary School",
  "reverse_geocoded_address": "450 North Liberty Street",
  "address_confidence": 0.88,
  "matched_zip": "43015",
  "jurisdiction": "City of Delaware",
  "needs_verification": false
}
```

## Core Functions

- `parse_transcript_for_location(text)` - Extracts raw address OR potential landmark name
- `validate_against_address_points(parsed_data)` - Compares parsed address to official Address Points
- `landmark_to_address(landmark_name)` - Searches datasets for landmark match
- `assign_zip_jurisdiction(address)` - Returns zip code, township, municipality
- `generate_validation_report(transcript)` - Full pipeline that processes transcript text to final output

## Performance Metrics

The engine tracks:
- Validation accuracy
- Address match confidence
- Landmark match confidence
- % of "needs verification" flags
- Number of "unknown" or unmatched cases
- Matched zip vs expected zip match rate
- Response latency per address resolution

## Validation Test Results

We tested the engine with a range of real-world emergency call scenarios that included both explicit addresses and landmark references. See `TEST_COMPARISON.md` for detailed results.

## Future Enhancements

See `IMPROVEMENT_ROADMAP.md` for detailed plans for future development. 
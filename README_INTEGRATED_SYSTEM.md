# AudioTranscripY + Validation Engine Integrated System

This system integrates the AudioTranscripY ML Interpretation layer with the Delaware County Address Validation Engine to create a complete emergency dispatch system.

## System Overview

The integrated system performs the following functions:
1. **Audio Call Processing**: Simulates or processes real audio calls to generate transcripts
2. **Address Validation**: Uses the validation engine to verify addresses, landmarks, and jurisdictions
3. **ML Interpretation**: Processes transcripts to extract incident type, casualty information, and priority
4. **Dispatch Report Generation**: Creates structured reports for emergency dispatchers

## Running the Integrated System

To run the complete integrated system:

```bash
python run_integrated_system.py
```

This will guide you through:
- Selecting or entering a transcript
- Validating the address with the validation engine
- Processing the transcript with ML interpretation
- Generating a dispatch report

## File Structure and Dependencies

The system requires the following key components:
- **validationengine/**: Contains the address validation engine and GIS data
- **ml_interpretation/**: Contains the ML interpretation system
- **run_integrated_system.py**: Main entry point for the integrated system

## Recommended Cleanup

The following files/directories are redundant and can be safely removed:

1. **Redundant Integration Files**:
   - `integrated_demo.py` (superseded by `run_integrated_system.py`)
   - `setup_validation_integration.py` (only needed for initial setup)
   - `connected_system.py` (older version of the integration)
   - `integration_setup.py` (superseded by setup_validation_integration.py)
   - `run_integration.sh` (shell script no longer needed)

2. **Redundant Test Files**:
   - `test_with_transcripts.py` (superseded by the integrated system)
   - `test_enhanced_features.py` (only needed during development)
   - `test_detailed_metrics.py` (only needed during development)

3. **Temporary Files**:
   - `addedfeatures.txt`
   - `i.txt`
   - `.DS_Store` files (macOS system files)

4. **Redundant Directories**:
   - `integration/` (old integration files)
   - `demo_outputs/` (test outputs no longer needed)
   - `test_outputs/` (test outputs no longer needed)
   - `interpretations/` (superseded by live_outputs/)

5. **In validationengine directory**:
   - `test_v2.py` (testing file no longer needed)
   - `test_multiple.py` (testing file no longer needed)
   - `test_address.py` (testing file no longer needed)
   - `i.txt` (temporary file)
   - The older `validation_engine.py` can be removed if `validation_engine_v2.py` is working as expected

## Dependencies

The system requires the following Python packages:
- fuzzywuzzy
- python-Levenshtein
- pandas
- numpy
- scikit-learn

Install them with:
```bash
pip install fuzzywuzzy python-Levenshtein pandas numpy scikit-learn
``` 
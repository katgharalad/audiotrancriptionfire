# AudioTranscripY + Delaware County Validation Engine - Project Inventory

This document provides a comprehensive inventory of all important files and directories in the project, organized by category.

## Core System Files

| File | Purpose |
|------|---------|
| `run_integrated_system.py` | Main integration script that orchestrates the audio transcription, validation, and ML interpretation workflow |
| `process_audio_file.py` | Processes pre-recorded audio files through the integrated system |
| `audio_simulation_transcription.py` | Simulates audio calls and processes them through the system |
| `real_time_audio_validation.py` | Provides real-time audio transcription and validation |
| `main.py` | Entry point for the application |
| `dispatcher_router.py` | Routes validated emergency data to the appropriate dispatchers |
| `emergency_processor.py` | Core logic for processing emergency data |
| `interpret_function.py` | Utility functions for interpretation of emergency data |

## Validation Engine Files

| File | Purpose |
|------|---------|
| `validationengine/validation_engine.py` | Original address validation engine implementation |
| `validationengine/validation_engine_v2.py` | Enhanced version of the validation engine with improved error handling and fallback mechanisms |
| `validationengine/run_validation.py` | Script to run the validation engine standalone |
| `validationengine/version_check.py` | Utility to verify validation engine version compatibility |
| `validationengine/setup_venv.py` | Script to set up the validation engine's virtual environment |
| `validationengine/__init__.py` | Package initialization file |

## ML Interpretation Files

| File | Purpose |
|------|---------|
| `ml_interpretation/interpreter.py` | Core ML interpretation logic for emergency data |
| `ml_interpretation/run_integration.py` | Script to run the ML interpretation layer standalone |
| `ml_interpretation/test_validation_integration.py` | Tests the integration between validation and ML interpretation |
| `ml_interpretation/whole_conversation_processor.py` | Processes complete emergency call conversations |
| `ml_interpretation/__init__.py` | Package initialization file |
| `interpretation_outputs/run_ml.py` | Script to run the ML interpretation on specific inputs |
| `interpretation_outputs/run_router.py` | Script to test the router functionality |

## Integration Files

| File | Purpose |
|------|---------|
| `integration/process_sample.py` | Processes sample data through the integrated system |
| `integration/run_integration.py` | Script to run the integration tests |
| `integration/whole_conversation_processor.py` | Processes complete conversations through the integrated system |

## Audio Processing Files

| File | Purpose |
|------|---------|
| `audio/LICENSE` | License for the audio processing component |
| `audio/README.md` | Documentation for the audio processing component |
| `audio/requirements.txt` | Dependencies for the audio processing component |
| `audio_simulator.py` | Simulates audio inputs for testing |

## Model and Evaluation Files

| File | Purpose |
|------|---------|
| `model_training.py` | Script for training the ML models |
| `evaluate_models.py` | Script for evaluating model performance |
| `visualize_results.py` | Generates visualizations of results |
| `explore_dataset.py` | Utilities for exploring the training datasets |
| `enhanced_features.py` | Implements enhanced feature extraction |
| `incident_model.pkl` | Serialized incident classification model |
| `casualties_model.pkl` | Serialized casualties prediction model |

## Data Files

| File | Purpose |
|------|---------|
| `data/delaware_addresses.csv` | Dataset of Delaware County addresses |
| `data/historical_priorities.csv` | Historical data on emergency priorities |
| `delaware_fire_incidents_full.csv` | Dataset of fire incidents in Delaware County |
| `validationengine/Address_Point_6449015960905250632 (1).csv` | GIS address point data |
| `validationengine/MSAG_155522220392559522.csv` | Master Street Address Guide data |
| `validationengine/Parcel_188782905266197535.csv` | Land parcel data |
| `validationengine/Street_Centerline_7861883908334951619.csv` | Street centerline GIS data |
| `validationengine/Zip_Code_-4600858990630826378.csv` | ZIP code boundary data |

## Output Directories

| Directory | Purpose |
|-----------|---------|
| `interpretations/` | Stores interpretation results |
| `interpretation_outputs/` | Stores processed interpretation outputs |
| `live_outputs/` | Stores results from live system runs |
| `test_outputs/` | Stores test run results |
| `demo_outputs/` | Stores outputs from demonstration runs |
| `audio_simulation/` | Stores audio simulation results |
| `plots/` | Stores generated data visualization plots |
| `reports/` | Stores system evaluation reports |
| `visualizations/` | Stores system visualization outputs |

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `VALIDATION_INTEGRATION.md` | Documentation of validation engine integration |
| `INTEGRATION.md` | Documentation of system integration |
| `validationengine/README.md` | Documentation for the validation engine |
| `validationengine/IMPROVEMENT_ROADMAP.md` | Future improvements for the validation engine |
| `validationengine/TEST_COMPARISON.md` | Validation engine test comparison results |
| `ml_interpretation/README.md` | Documentation for the ML interpretation layer |
| `ml_interpretation/VALIDATION_INTEGRATION.md` | Documentation of ML-validation integration |
| `integration/README.md` | Documentation for the integration components |

## Configuration and Utility Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Project dependencies |
| `.gitignore` | Specifies files to be ignored by Git |
| `cleanup_project.py` | Utility script for cleaning up project files |
| `finalize_upload.py` | Prepares the project for submission/upload |
| `real_time_gui.py` | GUI interface for real-time system operation |

## Sample and Test Files

| File | Purpose |
|------|---------|
| `sample_emergency_transcript.txt` | Sample emergency call transcript for testing |
| `sample_transcript.txt` | General sample transcript for testing |
| `test_transcript.txt` | Transcript used for system testing |
| `audio/sample_transcript.txt` | Sample transcript for audio processing tests |
| `audio/transcript_*.txt` | Generated transcripts from audio processing |
| `transcription_log.txt` | Log of transcription activities | 
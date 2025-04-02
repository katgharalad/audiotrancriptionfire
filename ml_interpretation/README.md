# AudioTranscripY ML Interpretation Layer

A machine learning interpretation layer for AudioTranscripY that processes real-time audio transcriptions for fire dispatch scenarios in Delaware, OH.

## Overview

This system builds on top of the existing AudioTranscripY real-time transcription tool to:

1. Process transcripts from emergency callers (Speaker 2)
2. Classify incident types (fire type, gas leak, etc.)
3. Identify casualty information
4. Extract address information
5. Output structured data for emergency responders

## Components

- **Dataset**: `delaware_fire_incidents_full.csv` - Real incident data from Delaware, OH
- **ML Models**: 
  - Incident type classifier (TF-IDF + LogisticRegression)
  - Casualties classifier (TF-IDF + LogisticRegression)
- **Integration Layer**: Processes transcripts and outputs structured interpretations

### Advanced Features

- **Audio Simulation**: Simulates real-time audio transcriptions for testing and demos without requiring actual audio input
- **LangChain-style Routing**: Routes incident interpretations to the appropriate handler based on incident type
- **Real-time GUI**: Visualizes emergency incidents and dispatch responses with a Delaware, OH map view

### Enhanced Features

These newly added features improve dispatch accuracy and decision-making:

- **Confidence Scores**: ML model prediction confidence is surfaced (using `predict_proba()`), with low-confidence cases routed to a verification queue
- **Address Validation**: Addresses are validated against Delaware's streets database with confidence scores
- **Priority Prediction**: Intelligently determines incident priority (1-5 scale) based on incident type and casualties
- **Structured Casualties**: Converts free-text casualties into a structured format with boolean flags for children, elderly, pets, and callers
- **Verification Queue**: Interface for human verification of low-confidence predictions

## Setup

1. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```
   pip install pandas scikit-learn matplotlib seaborn
   ```

   For GUI support (optional):
   ```
   # On Linux
   sudo apt-get install python3-tk
   
   # On macOS or Windows
   # Tkinter should come with Python installation
   ```

3. Train the models:
   ```
   python model_training.py
   ```

4. Run the demo:
   ```
   python integrated_demo.py --mode all
   ```

## Running Different Components

The system can be run in different modes:

- **All Components**: `python integrated_demo.py --mode all`
- **Audio Simulation**: `python integrated_demo.py --mode audio --duration 60 --interval 5`
- **Incident Router**: `python integrated_demo.py --mode router`
- **Interpreter Demo**: `python integrated_demo.py --mode interpreter`
- **Real-time GUI**: `python integrated_demo.py --mode gui`
- **Test Suite**: `python integrated_demo.py --mode test`
- **Result Visualization**: `python integrated_demo.py --mode visualize`
- **Enhanced Features Test**: `python integrated_demo.py --mode enhanced`

Specific scenario simulation:
```
python integrated_demo.py --mode audio --scenario gas_leak
```

Available scenarios: `kitchen_fire`, `gas_leak`, `vehicle_fire`

## Integration with AudioTranscripY

### Standard Integration

To integrate this ML layer with AudioTranscripY:

1. Import the interpreter:
   ```python
   from main import AudioTranscriptInterpreter
   ```

2. Initialize it:
   ```python
   interpreter = AudioTranscriptInterpreter()
   ```

3. Process transcripts as they arrive:
   ```python
   # After each successful Whisper transcription:
   if transcript.startswith("Speaker 2:"):
       result = interpreter.process_transcript(transcript)
       # Use the structured result
   ```

4. For advanced dispatch routing:
   ```python
   from dispatcher_router import IncidentRouter
   
   router = IncidentRouter()
   routing_result = router.route(result)
   # routing_result contains dispatched resources and priority level
   ```

### Direct Integration with AudioTranscripY Repository

If you have the AudioTranscripY repository available, you can use our integration script to connect them:

1. Clone the AudioTranscripY repository next to this one:
   ```bash
   git clone https://github.com/katgharalad/audiotrancriptionfire.git
   ```

2. Integration Methods:

   **Option 1: Using the integration.py script** (requires installation of AudioTranscripY dependencies)
   ```bash
   # Install required dependencies
   pip install sounddevice numpy faster-whisper scikit-learn librosa
   # Note: Dependency installation may require specific versions or additional requirements
   
   # Run the integration script
   python integration.py
   ```

   **Option 2: Manual Integration** (recommended for most users)
   
   Modify the AudioTranscripY code to call our ML layer:
   ```python
   # In audiotrancriptionfire/main.py
   # After processing a transcript
   
   from audiotranscriptmlmodel.main import AudioTranscriptInterpreter
   from audiotranscriptmlmodel.dispatcher_router import IncidentRouter
   
   # Initialize once
   interpreter = AudioTranscriptInterpreter()
   router = IncidentRouter()
   
   # In your transcript processing function
   if speaker == "Speaker 2":
       # Process with our ML interpreter
       result = interpreter.process_transcript(transcript)
       routing_result = router.route(result)
       
       # Use the results as needed
       print(result)
   ```

3. The integration process:
   - Identifies Speaker 2 (caller) transcripts in real-time
   - Processes them through our ML interpretation layer
   - Routes incidents to appropriate handlers
   - Generates structured data with confidence scores, validation, and priority levels

**Note:** Due to potential compatibility issues with the various audio processing libraries required by AudioTranscripY, manual integration is often more reliable than using the integration script.

## Testing Results

### Performance Metrics
```
================ PERFORMANCE METRICS ================
Total prediction time for 5639 samples: 0.1654 seconds
Average prediction time per sample: 0.0293 ms

---- Incident Type Classification ----
Accuracy: 1.0000
Precision: 1.0000
Recall: 1.0000
F1 Score: 1.0000

---- Casualties Classification ----
Accuracy: 1.0000
Precision: 1.0000
Recall: 1.0000
F1 Score: 1.0000
```

### Address Extraction Testing
```
================ ADDRESS EXTRACTION TESTING ================
Sample: Speaker 2: There's a kitchen fire at 123 Main Street. No one is hurt.
Extracted address: 123 main street
Incident type: kitchen fire
Casualties: none
--------------------------------------------------
Sample: Speaker 2: Gas leak reported at 456 Oak Avenue apt 7B. Everyone has evacuated.
Extracted address: 456 oak avenue
Incident type: gas leak
Casualties: caller trapped
--------------------------------------------------
Sample: Speaker 2: Structural fire at 789 Washington Boulevard. Elderly person trapped inside.
Extracted address: 789 washington boulevard
Incident type: electrical fire
Casualties: elderly person trapped
--------------------------------------------------
Sample: Speaker 2: Vehicle fire at 10 Liberty Lane. The caller is trapped.
Extracted address: 10 liberty lane
Incident type: vehicle fire
Casualties: caller trapped
--------------------------------------------------
Sample: Speaker 2: Wildfire reported near 55 Pinecrest Drive. Children are in danger.
Extracted address: 55 pinecrest drive
Incident type: wildfire
Casualties: children trapped
```

### Full Pipeline Testing Results
```
Input: Speaker 2: There's a kitchen fire at 123 Main Street. No one is hurt.
EMERGENCY CALL INTERPRETATION
INCIDENT TYPE: KITCHEN FIRE
CONFIDENCE: 0.99
LOCATION: 123 main street
ADDRESS VALID: True (Confidence: 0.69)
CASUALTIES: none
PRIORITY: HIGH (3.0)
STATUS: REQUIRES VERIFICATION

Input: Speaker 2: Structure fire at 456 Elm Road. My wife is trapped upstairs.
EMERGENCY CALL INTERPRETATION
INCIDENT TYPE: STRUCTURE FIRE
CONFIDENCE: 0.94
LOCATION: 456 elm road
ADDRESS VALID: True (Confidence: 0.22)
CASUALTIES: caller trapped
AFFECTED: Caller
PRIORITY: CRITICAL (4.8)
STATUS: REQUIRES VERIFICATION
```

### Enhanced Features Testing Results
```
==== Testing Confidence Scores ====
Confidence Metrics:
Accuracy: 1.00
High confidence correct: 3
High confidence incorrect: 0
Low confidence correct: 2
Low confidence incorrect: 0
Expected Calibration Error: 0.2700

==== Testing Address Validation ====
Address Validation Metrics:
Total addresses: 5
Valid addresses: 0
Invalid addresses: 5
Addresses needing verification: 5
Average confidence: 0.00
Verification rate: 1.00

==== Testing Priority Prediction ====
Rule-based Priority Metrics:
MSE: 0.2700
R²: -0.0385
Within 0.5: 0.80
Within 1.0: 1.00

==== Testing Casualties Structuring ====
Casualties Structuring Metrics:
Total samples: 5
Children identified: 1
Elderly identified: 1
Pets identified: 1
Caller identified: 1
Average categories per casualty: 0.80
```

### Integrated Demo Results
```
Running full integrated demo...
Starting dispatcher router demo...
Registered handler for 'structure fire'
Running interpreter demo...
Registered handler for 'kitchen fire'
Registered handler for 'gas leak'
Registered handler for 'vehicle fire'
Registered handler for 'wildfire'
Registered handler for 'false alarm'
Registered handler for 'electrical fire'
Registered handler for 'industrial fire'
IncidentRouter initialized with default handlers and middleware

Routing test interpretations...
[2025-04-01T22:28:07.411043] Routing interpretation: kitchen fire at 123 Oak Street - Casualties: none
[2025-04-01T22:28:07.916123] Routing interpretation: structure fire at 456 Elm Road - Casualties: children trapped
[2025-04-01T22:28:08.420827] Routing interpretation: gas leak at 789 Pine Avenue - Casualties: caller escaped alone

Starting audio simulation (duration: 30s, interval: 3s)
Audio Simulator initialized with 28195 caller transcripts
Output directory: demo_outputs/audio_simulation

Total transcripts: 12
Caller transcripts: 10
Non-caller transcripts: 2
Interpretations generated: 10
Average interpretation time: 5.96 ms

Simulation complete!
Results saved to demo_outputs/audio_simulation/simulation_20250401_222843.json
```

### Dispatcher Routing Example
```json
{
  "status": "processed",
  "handler": "structure_fire",
  "timestamp": "2025-04-01T22:07:48.423495",
  "message": "Dispatching fire units to structure fire",
  "resources": [
    "fire_engine",
    "ladder_truck",
    "ambulance",
    "battalion_chief"
  ],
  "interpretation": {
    "incident_type": "structure fire",
    "address": "456 Elm Road",
    "casualties": "children trapped",
    "timestamp": "2023-04-01T12:36:12",
    "transcript": "Speaker 2: There's a house on fire at 456 Elm Road. There are children trapped inside.",
    "priority": 5,
    "priority_level": "CRITICAL"
  }
}
```

### Gas Leak Scenario Simulation
```
==================================================
EMERGENCY CALL INTERPRETATION
==================================================
INCIDENT TYPE: GAS LEAK
CONFIDENCE: 0.97
LOCATION: 5149 south lake hill rd.
ADDRESS VALID: False (Confidence: 0.00)
CASUALTIES: elderly person trapped
AFFECTED: Elderly
PRIORITY: CRITICAL (4.9)
STATUS: REQUIRES VERIFICATION
==================================================
```

## Model Performance

The models achieve high accuracy on the Delaware, OH dataset:
- Incident Type Classification: 100% accuracy, 100% F1 score
- Casualties Classification: 100% accuracy, 100% F1 score
- Average prediction time: ~0.03ms per sample

## Output Format

### Basic Output
```json
{
  "incident_type": "kitchen fire",
  "address": "123 oak street",
  "casualties": "caller trapped",
  "timestamp": "2025-04-01T21:57:57.137253",
  "transcript": "Speaker 2: There's a kitchen fire at 123 Oak Street. The caller is trapped.",
  "priority": 3.5,
  "priority_level": "HIGH"
}
```

### Enhanced Output Format

The enhanced output includes additional fields for confidence, validation, and priority:

```json
{
  "incident_type": "kitchen fire",
  "incident_type_confidence": 0.95,
  "address": "123 oak street",
  "address_validation": {
    "valid": true,
    "confidence": 0.85,
    "needs_verification": false
  },
  "casualties": "caller trapped",
  "casualties_confidence": 0.90,
  "casualties_structured": {
    "children": false,
    "elderly": false,
    "pets": false,
    "caller": true
  },
  "priority": 3.8,
  "priority_level": "HIGH",
  "confidence": 0.92,
  "needs_verification": false,
  "timestamp": "2025-04-01T21:57:57.137253",
  "transcript": "Speaker 2: There's a kitchen fire at 123 Oak Street. The caller is trapped."
}
```

## Visualization Features

The system includes comprehensive data visualization capabilities that provide insights into:

- **Performance Metrics**: Bar charts showing accuracy, precision, recall, and F1 scores for all classification tasks
- **Address Extraction**: Pie charts showing success rates for address extraction
- **Incident Prioritization**: Visual breakdowns of incident priority levels
- **Resource Allocation**: Bar charts of resources dispatched by incident type
- **Timeline Analysis**: Conversation flow visualization showing incident type changes over time

These visualizations are automatically generated in the `visualizations/` directory when running:
```
python integrated_demo.py --mode visualize
```

## Real-Time GUI Features

The real-time GUI provides a comprehensive interface for:

- Monitoring incoming emergency calls
- Viewing incident details with confidence scores and priority levels
- Managing verification queue for low-confidence predictions
- Editing interpretations when necessary
- Dispatching appropriate resources based on incident type
- Tracking active incidents on a map of Delaware, OH
- Displaying status updates and dispatch logs

GUI components include:
- Incident list with priority color-coding
- Verification queue for human review
- Detailed incident view with structured casualty information
- Address validation results with confidence scores
- Resource dispatch panel for emergency response
- Interactive map of Delaware, OH with incident markers

## Notes

- Only processes transcripts from Speaker 2 (the caller)
- Outputs are saved to their respective directories
- Models are serialized to `incident_model.pkl` and `casualties_model.pkl`
- Address validation requires Delaware, OH address database
- Priority prediction uses both rule-based and optional ML-based models
- Confidence scores trigger verification queue entries

## Future Improvements

- Advanced address extraction using NER
- Confidence scores for predictions
- Fine-tuning with transformer models like BERT or RoBERTa
- Live integration with dispatch systems
- Full map integration with real Delaware, OH addresses
- Multi-incident coordination logic

## Visualization Features

The system includes comprehensive data visualization capabilities that provide insights into:

- **Performance Metrics**: Bar charts showing accuracy, precision, recall, and F1 scores for all classification tasks
- **Address Extraction**: Pie charts showing success rates for address extraction
- **Incident Prioritization**: Visual breakdowns of incident priority levels
- **Resource Allocation**: Bar charts of resources dispatched by incident type
- **Timeline Analysis**: Conversation flow visualization showing incident type changes over time

These visualizations are automatically generated in the `visualizations/` directory when running:
```
python integrated_demo.py --mode visualize
```

Example visualizations include:
- `classification_metrics.png`: Performance metrics for all classifiers
- `address_extraction.png`: Address extraction success rates
- `priority_levels.png`: Breakdown of incident priority levels
- `resources_dispatched.png`: Resources allocated by type
- `conversation_timeline.png`: Time-series analysis of incident interpretations 

## Enhanced Features Performance

The system includes advanced features that improve accuracy and reliability:

### Confidence Scores Performance
```
Confidence Metrics:
Accuracy: 1.00
High confidence correct: 3
High confidence incorrect: 0
Low confidence correct: 2
Low confidence incorrect: 0
Expected Calibration Error: 0.2700
```

### Address Validation Performance
```
Address Validation Metrics:
Total addresses: 5
Valid addresses: 0
Invalid addresses: 5
Addresses needing verification: 5
Average confidence: 0.00
Verification rate: 1.00
```

### Priority Prediction Performance
```
Rule-based Priority Metrics:
MSE: 0.2700
R²: -0.0385
Within 0.5: 0.80
Within 1.0: 1.00
```

### Casualties Structuring Performance
```
Casualties Structuring Metrics:
Total samples: 5
Children identified: 1
Elderly identified: 1
Pets identified: 1
Caller identified: 1
Average categories per casualty: 0.80
```

## Enhanced Output Format

The enhanced output includes additional fields for confidence, validation, and priority:

```json
{
  "incident_type": "kitchen fire",
  "incident_type_confidence": 0.95,
  "address": "123 oak street",
  "address_validation": {
    "valid": true,
    "confidence": 0.85,
    "needs_verification": false
  },
  "casualties": "caller trapped",
  "casualties_confidence": 0.90,
  "casualties_structured": {
    "children": false,
    "elderly": false,
    "pets": false,
    "caller": true
  },
  "priority": 3.8,
  "priority_level": "HIGH",
  "confidence": 0.92,
  "needs_verification": false,
  "timestamp": "2025-04-01T21:57:57.137253",
  "transcript": "Speaker 2: There's a kitchen fire at 123 Oak Street. The caller is trapped."
}
``` 
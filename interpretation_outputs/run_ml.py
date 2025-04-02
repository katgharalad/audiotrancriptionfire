
import os
import sys
import json
import re

# Add the project root directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

try:
    from main import AudioTranscriptInterpreter
    from enhanced_features import add_confidence_scores, needs_verification, AddressValidator, PriorityPredictor, CasualtyStructurer
except ModuleNotFoundError as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Get the input file path from command line
input_file = sys.argv[1]
output_file = sys.argv[2]

# Read the transcript
with open(input_file, 'r') as f:
    transcript = f.read().strip()

print(f"Processing transcript: {transcript}")

# Process with interpreter
try:
    interpreter = AudioTranscriptInterpreter(output_dir=os.path.dirname(output_file))
    result = interpreter.process_transcript(transcript)
    print(f"Interpretation result: {result}")
except Exception as e:
    print(f"Error during interpretation: {e}")
    result = None

# Apply enhanced features
if result:
    try:
        # Initialize enhanced features classes
        address_validator = AddressValidator()
        priority_predictor = PriorityPredictor()
        casualty_structurer = CasualtyStructurer()
        
        # Add mock probabilities since we don't have access to them
        mock_probabilities = {
            'incident_type_proba': [0.85],
            'casualties_proba': [0.80]
        }
        
        # Preserve "no children" information
        has_no_children = False
        if "no children" in transcript.lower() or "(no children)" in result.get('casualties', '').lower():
            has_no_children = True
            
        # Add confidence scores
        result = add_confidence_scores(result, mock_probabilities)
        
        # Validate address
        address_validation = address_validator.validate_address(result.get('address', ''))
        result['address_validation'] = address_validation
        
        # Predict priority
        priority, priority_level = priority_predictor.predict_priority(
            result.get('incident_type', ''),
            result.get('casualties', '')
        )
        result['priority'] = priority
        result['priority_level'] = priority_level
        
        # Structure casualties
        result['casualties_structured'] = casualty_structurer.structure_casualties(
            result.get('casualties', '')
        )
        
        # Override children flag if explicitly mentioned as not present
        if has_no_children and 'casualties_structured' in result:
            result['casualties_structured']['children'] = False
            result['casualties'] = result['casualties'].replace('children', 'adults')
            if 'text' in result['casualties_structured']:
                result['casualties_structured']['text'] = result['casualties_structured']['text'].replace('children', 'adults')
        
        # Check if verification is needed
        result['needs_verification'] = needs_verification(result)
        
        # Save the result
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("ML interpretation completed successfully.")
    except Exception as e:
        print(f"Error applying enhanced features: {e}")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
else:
    print("ML interpretation failed - no result returned.")
    # Create an empty result file
    with open(output_file, 'w') as f:
        f.write("{}")

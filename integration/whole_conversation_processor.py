#!/usr/bin/env python3
"""
This script processes entire transcripts regardless of speaker labels.
It extracts emergency incident information from the whole conversation context.
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime

class ConversationProcessor:
    def __init__(self, transcript_path=None):
        self.transcript_path = transcript_path
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conversation_text = ""
        self.transcript_lines = []
        
        # Initialize output directory
        self.output_dir = os.path.join(self.current_dir, "interpretation_outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create standard patterns for extracting information
        self.address_pattern = re.compile(r'\b(\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|circle|cir|place|pl|court|ct|boulevard|blvd|highway|hwy|way|parkway|pkwy))\b', re.IGNORECASE)
        self.incident_types = [
            "kitchen fire", "structure fire", "gas leak", "vehicle fire", "wildfire",
            "electrical fire", "industrial fire", "false alarm"
        ]
    
    def load_transcript(self, transcript_path=None):
        """Load the transcript from a file."""
        if transcript_path:
            self.transcript_path = transcript_path
        
        if not self.transcript_path or not os.path.exists(self.transcript_path):
            print(f"Error: Transcript file not found at {self.transcript_path}")
            return False
        
        print(f"Loading transcript from: {self.transcript_path}")
        
        # Read the transcript
        with open(self.transcript_path, "r") as f:
            self.transcript_lines = f.readlines()
        
        # Extract the entire conversation text
        self.conversation_text = ""
        collecting_content = False
        
        for line in self.transcript_lines:
            line = line.strip()
            
            # Start collecting content after the header section
            if "LIVE TRANSCRIPTION" in line:
                collecting_content = True
                continue
                
            # Skip headers, separators and empty lines
            if not collecting_content or not line or line.startswith("===") or line.startswith("---"):
                continue
                
            # Skip timestamp prefix (like "00:31:23: ")
            if re.match(r'^\d{2}:\d{2}:\d{2}:\s+', line):
                content = re.sub(r'^\d{2}:\d{2}:\d{2}:\s+', '', line)
                self.conversation_text += content + " "
            # Otherwise add the line as is (if it's not a separator)
            elif not all(c == '-' or c == '=' for c in line):
                self.conversation_text += line + " "
        
        print(f"\nExtracted {len(self.conversation_text)} characters of conversation text.")
        print(f"\nConversation preview: \"{self.conversation_text[:150]}...\"")
        return True
    
    def extract_incident_info(self):
        """Extract emergency incident information from the conversation."""
        if not self.conversation_text:
            print("No conversation text loaded.")
            return None
        
        print("\n" + "-"*70)
        print("EXTRACTING INCIDENT INFORMATION".center(70))
        print("-"*70)
        
        # Extract address using regex pattern
        address_matches = self.address_pattern.findall(self.conversation_text)
        address = address_matches[0] if address_matches else "unknown address"
        
        # Identify incident type by checking for keywords
        incident_type = "unknown"
        
        # Check for gas leak first (higher priority)
        if "gas leak" in self.conversation_text.lower() or ("gas" in self.conversation_text.lower() and "leak" in self.conversation_text.lower()):
            incident_type = "gas leak"
        # Otherwise check for other incidents
        else:
            for itype in self.incident_types:
                if itype in self.conversation_text.lower():
                    incident_type = itype
                    break
        
        # If still unknown but contains "fire", determine the type
        if incident_type == "unknown" and "fire" in self.conversation_text.lower():
            if "kitchen" in self.conversation_text.lower() or "stove" in self.conversation_text.lower():
                incident_type = "kitchen fire"
            elif "home" in self.conversation_text.lower() or "house" in self.conversation_text.lower():
                incident_type = "structure fire"
            else:
                incident_type = "structure fire"
        
        # Check for casualties and people/animals in danger
        casualties = "none"
        
        # Check for specific casualty counts first
        casualty_patterns = [
            r'(\d+)\s+casualt(?:y|ies)',       # "2 casualties"
            r'(\d+)\s+(?:person|people)\s+(?:injured|hurt)',  # "2 people injured"
            r'(\d+)\s+(?:is|are)\s+(?:injured|hurt)',         # "2 are injured"
            r'there\s+(?:is|are)\s+(\d+)\s+casualt(?:y|ies)', # "there are 2 casualties"
        ]
        
        for pattern in casualty_patterns:
            match = re.search(pattern, self.conversation_text.lower())
            if match:
                count = match.group(1)
                casualties = f"{count} casualties"
                break
                
        # If no specific count found, check for general casualties
        if casualties == "none" and "casualties" in self.conversation_text.lower():
            if re.search(r'\b(?:no|not|zero)\s+casualties\b', self.conversation_text.lower()):
                casualties = "none"
            else:
                casualties = "people injured"
        
        # Check for trapped individuals
        if "trapped" in self.conversation_text.lower():
            trapped_patterns = [
                r'(\d+)\s+(?:people|person|individuals|victims)?\s+(?:are|is)?\s+(?:still)?\s+trapped',  # "3 people trapped"
                r'trapped\s+(\d+)',  # "trapped 3"
                r'there\s+(?:is|are)\s+(\d+)\s+(?:people|person|individuals|victims)?\s+trapped'  # "there are 3 people trapped"
            ]
            
            for pattern in trapped_patterns:
                match = re.search(pattern, self.conversation_text.lower())
                if match:
                    count = match.group(1)
                    casualties = f"{count} people trapped"
                    break
            
            # If no count found, determine the type of trapped individuals
            if "trapped" in casualties:
                # Already set with count
                pass
            elif "dog" in self.conversation_text.lower() or "pet" in self.conversation_text.lower():
                casualties = "pets trapped"
            elif any(re.search(pattern, self.conversation_text.lower()) for pattern in [r'\bno\s+children\b', r'only\s+adults\b', r'just\s+adults\b']):
                casualties = "adults trapped"
            elif any(word in self.conversation_text.lower() for word in ["child", "children", "kid", "kids", "baby", "babies"]):
                casualties = "children trapped"
            elif "alone" in self.conversation_text.lower() or "myself" in self.conversation_text.lower():
                casualties = "caller trapped"
            else:
                casualties = "people trapped"
        
        # Specifically check for information about children
        has_children = False
        no_children = False
        
        # First check if it explicitly says no children
        if any(re.search(pattern, self.conversation_text.lower()) for pattern in 
               [r'\bno\s+children\b', r'only\s+adults\b', r'just\s+adults\b', r'no\s+kids\b']):
            no_children = True
        
        # Then check if children are mentioned positively
        if any(word in self.conversation_text.lower() for word in ["child", "children", "kid", "kids", "baby", "babies"]):
            if not no_children:
                has_children = True
                
        # Check for child involvement
        if "children involved" in self.conversation_text.lower() and casualties == "none":
            casualties = "children involved"
        
        # Modify casualties based on children information
        if "trapped" in casualties and no_children:
            casualties = casualties.replace("trapped", "trapped (no children)")
        elif "trapped" in casualties and has_children and "children" not in casualties:
            casualties = "children trapped"
        
        # Create a structured interpretation
        interpretation = {
            "incident_type": incident_type,
            "address": address,
            "casualties": casualties,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "transcript": self.conversation_text[:500] + "..." if len(self.conversation_text) > 500 else self.conversation_text
        }
        
        print("\n==================================================")
        print("EMERGENCY CALL INTERPRETATION")
        print("==================================================")
        print(f"INCIDENT TYPE: {interpretation['incident_type'].upper()}")
        print(f"LOCATION: {interpretation['address']}")
        print(f"CASUALTIES: {interpretation['casualties']}")
        print("==================================================\n")
        
        return interpretation
    
    def apply_ml_interpretation(self, interpretation):
        """Use the ML interpretation layer to enhance the basic interpretation."""
        if not interpretation:
            return interpretation
        
        print("\n" + "-"*70)
        print("APPLYING ML INTERPRETATION LAYER".center(70))
        print("-"*70)
        
        # Create a simplified transcript for the ML layer to process
        simplified_transcript = f"Speaker 2: There's a {interpretation['incident_type']} at {interpretation['address']}. {interpretation['casualties']}."
        
        # Save it to a file to avoid command line escaping issues
        ml_input_file = os.path.join(self.output_dir, "ml_input.txt")
        with open(ml_input_file, "w") as f:
            f.write(simplified_transcript)
        
        try:
            # Create a Python script for the ML interpreter
            ml_script = os.path.join(self.output_dir, "run_ml.py")
            with open(ml_script, "w") as f:
                f.write("""
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
""")
            
            # Create output file path
            ml_output_file = os.path.join(self.output_dir, "ml_result.json")
            
            # Run the command
            cmd_parts = [
                f"cd '{self.current_dir}'",
                "source venv/bin/activate",
                f"PYTHONPATH='{self.current_dir}' python {ml_script} {ml_input_file} {ml_output_file}"
            ]
            command = " && ".join(cmd_parts)
            print(f"Executing: {command}")
            subprocess.run(command, shell=True, check=True)
            
            # Read the result
            if os.path.exists(ml_output_file) and os.path.getsize(ml_output_file) > 2:  # more than just "{}"
                with open(ml_output_file, 'r') as f:
                    enhanced_result = json.load(f)
                
                # Merge with our basic interpretation, keeping conversation text
                enhanced_result["transcript"] = interpretation["transcript"]
                
                # Check if the transcript explicitly mentions 'no children'
                if "no children" in interpretation["transcript"].lower() and 'casualties_structured' in enhanced_result:
                    enhanced_result['casualties_structured']['children'] = False
                    # If casualties mentions children but transcript says no children, correct it
                    if 'children' in enhanced_result.get('casualties', '').lower():
                        enhanced_result['casualties'] = enhanced_result['casualties'].replace('children', 'adults')
                
                # Display the enhanced interpretation
                print("\n==================================================")
                print("ENHANCED EMERGENCY CALL INTERPRETATION")
                print("==================================================")
                print(f"INCIDENT TYPE: {enhanced_result.get('incident_type', 'UNKNOWN').upper()}")
                if 'confidence' in enhanced_result:
                    print(f"CONFIDENCE: {enhanced_result.get('confidence', 0):.2f}")
                print(f"LOCATION: {enhanced_result.get('address', 'unknown address')}")
                
                # Address validation
                addr_valid = enhanced_result.get('address_validation', {})
                if addr_valid:
                    print(f"ADDRESS VALID: {addr_valid.get('valid', False)} (Confidence: {addr_valid.get('confidence', 0):.2f})")
                
                # Casualties
                print(f"CASUALTIES: {enhanced_result.get('casualties', 'none')}")
                
                # Structured casualties
                cas = enhanced_result.get('casualties_structured', {})
                if cas:
                    affected = []
                    if cas.get('children', False): affected.append("Children")
                    if cas.get('elderly', False): affected.append("Elderly")
                    if cas.get('pets', False): affected.append("Pets")
                    if cas.get('caller', False): affected.append("Caller")
                    if affected:
                        print(f"AFFECTED: {', '.join(affected)}")
                
                # Priority
                if 'priority' in enhanced_result:
                    priority_val = enhanced_result.get('priority', 0)
                    priority_level = enhanced_result.get('priority_level', 'UNKNOWN')
                    print(f"PRIORITY: {priority_level} ({priority_val})")
                print("==================================================\n")
                
                return enhanced_result
            else:
                print("No structured result found in ML output file.")
        except subprocess.CalledProcessError as e:
            print(f"Error running ML interpreter: {e}")
        except Exception as e:
            print(f"Error processing ML result: {e}")
        
        # Return the original interpretation if ML enhancement failed
        return interpretation
    
    def route_incident(self, interpretation):
        """Route the incident to the appropriate handler using the dispatcher router."""
        if not interpretation:
            return None
        
        print("\n" + "-"*70)
        print("DISPATCHER ROUTING".center(70))
        print("-"*70)
        
        try:
            # Save the interpretation to a temporary file
            temp_file = os.path.join(self.output_dir, "temp_interpretation.json")
            with open(temp_file, "w") as f:
                json.dump(interpretation, f, indent=2)
            
            # Create a Python script for the router
            router_script = os.path.join(self.output_dir, "run_router.py")
            with open(router_script, "w") as f:
                f.write("""
import os
import sys
import json

# Add the project root directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

try:
    from dispatcher_router import IncidentRouter
except ModuleNotFoundError as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Get the input file path from command line
input_file = sys.argv[1]
output_file = sys.argv[2]

# Read the interpretation
with open(input_file, 'r') as f:
    interpretation = json.load(f)

print(f"Routing incident: {interpretation}")

# Route the incident
try:
    router = IncidentRouter()
    routing_result = router.route(interpretation)
    
    # Save the result
    with open(output_file, 'w') as f:
        json.dump(routing_result, f, indent=2)
    
    print("Routing completed successfully.")
except Exception as e:
    print(f"Error during routing: {e}")
    # Create an empty result file
    with open(output_file, 'w') as f:
        json.dump({}, f)
""")
            
            # Create output file path
            router_output_file = os.path.join(self.output_dir, "router_result.json")
            
            # Run the command
            cmd_parts = [
                f"cd '{self.current_dir}'",
                "source venv/bin/activate",
                f"PYTHONPATH='{self.current_dir}' python {router_script} {temp_file} {router_output_file}"
            ]
            command = " && ".join(cmd_parts)
            print(f"Executing: {command}")
            subprocess.run(command, shell=True, check=True)
            
            # Read the result
            if os.path.exists(router_output_file) and os.path.getsize(router_output_file) > 2:
                with open(router_output_file, 'r') as f:
                    routing_result = json.load(f)
                
                # Display the routing result
                print(f"\nRouting result:")
                print(f"  Status: {routing_result.get('status', 'unknown')}")
                print(f"  Handler: {routing_result.get('handler', 'unknown')}")
                print(f"  Message: {routing_result.get('message', 'No message')}")
                print(f"  Resources dispatched:")
                for resource in routing_result.get('resources', []):
                    print(f"    - {resource.replace('_', ' ').title()}")
                
                return routing_result
            else:
                print("No routing result found in output file.")
        except subprocess.CalledProcessError as e:
            print(f"Error routing incident: {e}")
        except Exception as e:
            print(f"Error processing routing result: {e}")
        
        return None
    
    def save_results(self, interpretation, routing_result):
        """Save the interpretation and routing results to a file."""
        if not interpretation:
            return
        
        # Create the full result object
        full_result = {
            "interpretation": interpretation,
            "routing": routing_result if routing_result else {}
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(self.output_dir, f"conversation_interpretation_{timestamp}.json")
        with open(results_file, "w") as f:
            json.dump(full_result, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
    
    def process(self, transcript_path=None):
        """Process the transcript and generate interpretations."""
        if transcript_path:
            self.transcript_path = transcript_path
        
        # Load the transcript
        if not self.load_transcript():
            return
        
        # Extract basic incident information
        basic_interpretation = self.extract_incident_info()
        
        # Apply ML interpretation layer for enhancements
        enhanced_interpretation = self.apply_ml_interpretation(basic_interpretation)
        
        # Route the incident
        routing_result = self.route_incident(enhanced_interpretation)
        
        # Save results
        self.save_results(enhanced_interpretation, routing_result)
        
        print("\n" + "="*70)
        print("CONVERSATION PROCESSING COMPLETE".center(70))
        print("="*70 + "\n")


def main():
    print("\n" + "="*70)
    print("WHOLE CONVERSATION PROCESSOR".center(70))
    print("="*70 + "\n")
    
    # Get path to sample transcript
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_transcript = os.path.join(current_dir, "audiotranscript copy", "sample_transcript.txt")
    
    # Check if a transcript was provided as a command-line argument
    transcript_path = sys.argv[1] if len(sys.argv) > 1 else default_transcript
    
    # Process the transcript
    processor = ConversationProcessor(transcript_path)
    processor.process()


if __name__ == "__main__":
    main() 
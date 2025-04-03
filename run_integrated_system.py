#!/usr/bin/env python3
import os
import sys
import json
import time
import random
import datetime
from pathlib import Path
import re

# Make sure the validation engine and ml_interpretation are in the path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

validation_dir = os.path.join(script_dir, "validationengine")
ml_dir = os.path.join(script_dir, "ml_interpretation")

# Add paths
if validation_dir not in sys.path:
    sys.path.insert(0, validation_dir)
if ml_dir not in sys.path:
    sys.path.insert(0, ml_dir)

def load_sample_transcripts():
    """Load sample emergency call transcripts."""
    # These are some example emergency call transcripts
    return [
        "Speaker 2: I'm seeing flames coming from Smith Elementary School. The kids are outside but there's a lot of smoke.",
        "Speaker 2: There's a car accident at 162 Muirwood Village Drive. Two vehicles, looks like people are trapped inside.",
        "Speaker 2: I'm at 123 Main Street and my neighbor's house has smoke coming from the windows.",
        "Speaker 2: Fire behind Liberty Township Fire Station, it's spreading fast!",
        "Speaker 2: I'm at the Kroger on North Houk Road, there's been an explosion in the parking lot.",
        "Speaker 2: There's a medical emergency at 450 North Liberty Street, an elderly person has collapsed.",
        "Speaker 2: I'm at the Delaware County EMS station. Someone just crashed their car into the building!",
        "Speaker 2: Gas smell at 64 W Winter Street apartment building. Everyone is evacuating.",
        "Speaker 2: There's water pouring out of Hayes High School, looks like a major pipe burst.",
        "Speaker 2: I'm outside 242 Spring Street. The house is on fire and I think someone is still inside!"
    ]

def simulate_audio_call():
    """Simulate an audio call and return a transcript."""
    print("\n" + "="*70)
    print("AUDIO CALL SIMULATION".center(70))
    print("="*70)
    
    # Load sample transcripts
    transcripts = load_sample_transcripts()
    
    # Ask if user wants to use a sample or provide their own
    print("\nDo you want to:")
    print("1. Use a randomly selected sample transcript")
    print("2. Choose from sample transcripts")
    print("3. Enter your own transcript")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        # Random sample
        transcript = random.choice(transcripts)
        print(f"\nSelected transcript: \"{transcript}\"")
    
    elif choice == '2':
        # Choose from samples
        print("\nAvailable transcripts:")
        for i, t in enumerate(transcripts):
            print(f"{i+1}. {t}")
        
        idx = int(input("\nSelect transcript number: ").strip()) - 1
        if 0 <= idx < len(transcripts):
            transcript = transcripts[idx]
            print(f"\nSelected transcript: \"{transcript}\"")
        else:
            print("Invalid selection. Using a random transcript.")
            transcript = random.choice(transcripts)
            print(f"\nSelected transcript: \"{transcript}\"")
    
    elif choice == '3':
        # Custom transcript
        print("\nEnter your custom transcript (must start with 'Speaker 2:'):")
        transcript = input("> ").strip()
        if not transcript.startswith("Speaker 2:"):
            transcript = "Speaker 2: " + transcript
    
    else:
        # Default to random
        transcript = random.choice(transcripts)
        print(f"\nInvalid choice. Using a random transcript: \"{transcript}\"")
    
    # Simulate processing time
    print("\nSimulating audio processing...")
    for i in range(5):
        print(".", end="", flush=True)
        time.sleep(0.3)
    
    print(f"\n\nFinal transcript: \"{transcript}\"")
    
    return transcript

def validate_address(transcript):
    """Validate and enrich address information using the validation engine."""
    print("\n" + "="*70)
    print("ADDRESS VALIDATION".center(70))
    print("="*70)
    
    print("\nInitializing validation engine...")
    
    try:
        # Import the validation engine
        from validation_engine_v2 import AddressValidationEngine
        
        # Initialize the engine with the directory containing the data files
        engine = AddressValidationEngine(data_dir=validation_dir)
        
        # Generate validation report
        print("\nValidating address information...")
        result = engine.generate_validation_report(transcript)
        
        print("\nValidation Results:")
        print(f"Address Validity: {result.get('address_validity', False)}")
        print(f"Matched Address: {result.get('matched_address', 'Unknown')}")
        print(f"Landmark: {result.get('matched_landmark', 'None')}")
        print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"ZIP Code: {result.get('zip_code', 'Unknown')}")
        print(f"Jurisdiction: {result.get('jurisdiction', 'Unknown')}")
        print(f"Needs Verification: {result.get('needs_verification', True)}")
        print(f"Processing Time: {result.get('processing_time_ms', 0)} ms")
        
        return result
    
    except Exception as e:
        print(f"\nError during address validation: {e}")
        import traceback
        traceback.print_exc()
        
        # Return basic structure with error
        return {
            'address_validity': False,
            'matched_address': "Error processing address",
            'matched_landmark': None,
            'confidence_score': 0.0,
            'zip_code': None,
            'jurisdiction': None,
            'needs_verification': True,
            'error': str(e)
        }

def generate_ml_interpretation(transcript, validation_result):
    """
    Process transcript with ML interpretation, enhanced with validation results.
    """
    print("\n" + "="*70)
    print("ML INTERPRETATION".center(70))
    print("="*70)
    
    try:
        # First try to import from our custom interpreter
        try:
            from ml_interpretation.interpreter import AudioTranscriptInterpreter
            print("\nUsing integrated interpreter from ml_interpretation module")
            
            # Create output directory
            output_dir = os.path.join(script_dir, "live_outputs", "integrated_system")
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize the interpreter
            interpreter = AudioTranscriptInterpreter(output_dir=output_dir)
            
            # Process the transcript (this will automatically use validation)
            interpretation = interpreter.process_transcript(transcript)
            
            return interpretation
        
        except ImportError:
            print("\nML interpretation module not found. Using basic interpretation.")
            
            # Basic interpretation without ML
            basic_interpretation = {
                "incident_type": "unknown incident",
                "address": validation_result.get('matched_address', 'Unknown address'),
                "casualties": "unknown",
                "timestamp": datetime.datetime.now().isoformat(),
                "transcript": transcript
            }
            
            # Enrich with validation data
            basic_interpretation.update({
                "reverse_geocoded_address": validation_result.get('matched_address', 'Unknown address'),
                "landmark": validation_result.get('matched_landmark'),
                "address_confidence": validation_result.get('confidence_score', 0.0),
                "matched_zip": validation_result.get('zip_code'),
                "jurisdiction": validation_result.get('jurisdiction'),
                "needs_verification": validation_result.get('needs_verification', True)
            })
            
            return basic_interpretation
    
    except Exception as e:
        print(f"\nError during ML interpretation: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a minimal result in case of error
        return {
            "incident_type": "error",
            "address": validation_result.get('matched_address', 'Unknown address'),
            "casualties": "unknown",
            "error": str(e),
            "transcript": transcript,
            "timestamp": datetime.datetime.now().isoformat()
        }

def generate_dispatch_report(interpretation):
    """Generate a final dispatch report based on ML interpretation."""
    print("\n" + "="*70)
    print("DISPATCH REPORT GENERATION".center(70))
    print("="*70)
    
    # Extract key information
    incident_type = interpretation.get('incident_type', 'unknown incident').upper()
    
    # Get address information
    address = interpretation.get('reverse_geocoded_address', interpretation.get('address', 'Unknown location'))
    transcript = interpretation.get('transcript', '')
    
    # If the address is incomplete or just a number, use the transcript to extract a better address
    if address == "Unknown address" or address.isdigit() or '   ' in address:
        # First, look for explicit street patterns
        street_pattern = r'(\d+\s+(?:[NSEW]\s+)?[A-Za-z\s\-]+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Court|Ct|Lane|Ln|Way|Boulevard|Blvd|Circle|Cir|Place|Pl|Terrace|Ter|Trail|Tr|Highway|Hwy|Parkway|Pkwy))'
        street_matches = re.findall(street_pattern, transcript, re.IGNORECASE)
        
        # Then try a simpler pattern for street names without type (like "Spring Street")
        simple_pattern = r'(\d+\s+(?:[NSEW]\s+)?[A-Za-z]+(?:\s+[A-Za-z]+){1,2})'
        simple_matches = re.findall(simple_pattern, transcript, re.IGNORECASE)
        
        # First, look for exact house number matches if we have a numeric address
        house_number = None
        if address.isdigit():
            house_number = address
        elif '   ' in address and address.strip().split()[0].isdigit():
            house_number = address.strip().split()[0]
        
        if house_number:
            # Look for exact house number matches
            for match in street_matches + simple_matches:
                if match.strip().startswith(house_number + " "):
                    address = match.strip()
                    print(f"Enhanced address from transcript: {address}")
                    break
        else:
            # Without a house number, just use the first good match if any
            all_matches = street_matches + simple_matches
            if all_matches:
                address = all_matches[0].strip()
                print(f"Enhanced address from transcript: {address}")
    
    landmark = interpretation.get('landmark', '')
    address_info = f"{address}{f' (Landmark: {landmark})' if landmark else ''}"
    jurisdiction = interpretation.get('jurisdiction', None) or 'Unknown jurisdiction'
    zip_code = interpretation.get('matched_zip', '')
    casualties = interpretation.get('casualties', 'unknown')
    priority = interpretation.get('priority', 3.0)
    priority_level = interpretation.get('priority_level', 'MEDIUM')
    confidence = interpretation.get('address_confidence', 0.0)
    verification = "REQUIRES VERIFICATION" if interpretation.get('needs_verification', True) else "VERIFIED"
    
    # Determine required resources based on incident type
    resources = []
    if 'fire' in incident_type.lower():
        resources.extend(["FIRE_ENGINE", "LADDER_TRUCK", "PARAMEDICS"])
        if 'structure' in incident_type.lower():
            resources.append("HAZMAT_TEAM")
    elif 'medical' in incident_type.lower():
        resources.append("AMBULANCE")
    elif 'accident' in incident_type.lower() or 'crash' in incident_type.lower():
        resources.extend(["AMBULANCE", "FIRE_ENGINE", "POLICE"])
    elif 'gas' in incident_type.lower() or 'explosion' in incident_type.lower():
        resources.extend(["FIRE_ENGINE", "HAZMAT_TEAM", "PARAMEDICS", "POLICE"])
    else:
        resources.extend(["FIRE_ENGINE", "PARAMEDICS"])  # Default
    
    # Create the dispatch report
    dispatch_report = {
        "dispatch_id": f"DISP-{int(time.time())}",
        "timestamp": datetime.datetime.now().isoformat(),
        "dispatch_status": "PENDING",
        "incident": {
            "type": incident_type,
            "description": interpretation.get('transcript', '').replace("Speaker 2: ", ""),
            "location": {
                "address": address,
                "landmark": landmark,
                "jurisdiction": jurisdiction,
                "zip_code": zip_code,
                "coordinates": None  # Would be filled in a real system
            },
            "casualties": casualties,
            "priority": priority,
            "priority_level": priority_level
        },
        "response": {
            "resources_required": resources,
            "estimated_arrival_time": "UNKNOWN",
            "special_instructions": f"Address confidence: {confidence:.2f} - {verification}"
        },
        "validation": {
            "address_confidence": confidence,
            "needs_verification": interpretation.get('needs_verification', True),
            "validation_time_ms": interpretation.get('processing_time_ms', 0)
        }
    }
    
    # Save the dispatch report
    output_dir = os.path.join(script_dir, "live_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    report_file = os.path.join(output_dir, f"dispatch_report_{int(time.time())}.json")
    with open(report_file, 'w') as f:
        json.dump(dispatch_report, f, indent=2)
    
    print(f"\nDispatch report saved to: {report_file}")
    
    # Print a formatted report
    print("\n" + "="*70)
    print("EMERGENCY DISPATCH REPORT".center(70))
    print("="*70)
    print(f"INCIDENT TYPE: {incident_type}")
    print(f"LOCATION: {address_info}")
    print(f"JURISDICTION: {jurisdiction}")
    if zip_code:
        print(f"ZIP CODE: {zip_code}")
    print(f"CASUALTIES: {casualties}")
    print(f"PRIORITY: {priority_level} ({priority})")
    print(f"\nRESOURCES DISPATCHED:")
    for resource in resources:
        print(f"  - {resource.replace('_', ' ')}")
    print(f"\nSTATUS: {verification}")
    print("="*70)
    
    return dispatch_report

def main():
    """Main function to run the integrated system."""
    print("\n" + "="*70)
    print("AUDIOTRANSCRIPY + VALIDATION ENGINE INTEGRATED SYSTEM".center(70))
    print("="*70)
    
    # Step 1: Simulate audio call and get transcript
    transcript = simulate_audio_call()
    
    # Step 2: Validate address information using the validation engine
    validation_result = validate_address(transcript)
    
    # Step 3: Process with ML interpretation, enhanced with validation results
    interpretation = generate_ml_interpretation(transcript, validation_result)
    
    # Step 4: Generate final dispatch report
    dispatch_report = generate_dispatch_report(interpretation)
    
    print("\nIntegrated system processing complete!")
    print("A dispatcher would now receive this report and coordinate the response.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
#!/usr/bin/env python3
import os
import sys
import time
import datetime
import json
import re
import argparse

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

# Create necessary directories
output_dir = os.path.join(script_dir, "live_outputs", "audio_transcription")
os.makedirs(output_dir, exist_ok=True)

def process_transcript(transcript):
    """Process a transcript through validation and ML interpretation."""
    # Import validation and interpretation modules
    try:
        from validation_engine_v2 import AddressValidationEngine
        from ml_interpretation.interpreter import AudioTranscriptInterpreter
        
        validation_engine = AddressValidationEngine(data_dir=validation_dir)
        interpreter = AudioTranscriptInterpreter(output_dir=output_dir)
        
        print("Validation engine and ML interpretation modules loaded successfully.")
    except Exception as e:
        print(f"Error loading validation or interpretation modules: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Prepare transcript
    if "Speaker 2:" not in transcript:
        transcript_to_process = "Speaker 2: " + transcript
    else:
        transcript_to_process = transcript
    
    print("\n" + "="*70)
    print("PROCESSING TRANSCRIPT".center(70))
    print("="*70)
    print(f"Transcript: {transcript_to_process}")
    
    # Validate address
    try:
        print("\nValidating address...")
        validation_result = validation_engine.generate_validation_report(transcript_to_process)
        
        # Process interpretation
        print("\nGenerating interpretation...")
        interpretation = interpreter.process_transcript(transcript_to_process)
        
        # Generate and save report
        timestamp = int(time.time())
        report_file = os.path.join(output_dir, f"emergency_report_{timestamp}.json")
        
        # Extract address from validation result
        address = validation_result.get('matched_address', 'Unknown address')
        
        # Enhance address if needed
        if address == "Unknown address" or address.isdigit() or '   ' in address:
            enhanced_address = enhance_address_from_transcript(transcript_to_process, address)
            if enhanced_address:
                address = enhanced_address
                print(f"Enhanced address from transcript: {address}")
        
        # Create dispatch report
        dispatch_report = {
            "transcript": transcript_to_process,
            "timestamp": datetime.datetime.now().isoformat(),
            "address": address,
            "landmark": validation_result.get('matched_landmark'),
            "zip_code": validation_result.get('zip_code'),
            "jurisdiction": validation_result.get('jurisdiction'),
            "incident_type": interpretation.get('incident_type', 'unknown'),
            "priority": interpretation.get('priority', 3.0),
            "needs_verification": validation_result.get('needs_verification', True)
        }
        
        with open(report_file, 'w') as f:
            json.dump(dispatch_report, f, indent=2)
        
        # Print report
        print("\n" + "="*70)
        print("EMERGENCY DISPATCH REPORT".center(70))
        print("="*70)
        print(f"INCIDENT: {dispatch_report['incident_type'].upper()}")
        print(f"LOCATION: {address}")
        if dispatch_report['landmark']:
            print(f"LANDMARK: {dispatch_report['landmark']}")
        if dispatch_report['jurisdiction']:
            print(f"JURISDICTION: {dispatch_report['jurisdiction']}")
        if dispatch_report['zip_code']:
            print(f"ZIP CODE: {dispatch_report['zip_code']}")
        print(f"PRIORITY: {dispatch_report['priority']}")
        verification = "REQUIRES VERIFICATION" if dispatch_report['needs_verification'] else "VERIFIED"
        print(f"STATUS: {verification}")
        print("="*70)
        print(f"Report saved to: {report_file}")
        
        return dispatch_report
        
    except Exception as e:
        print(f"Error processing emergency: {e}")
        import traceback
        traceback.print_exc()
        return None

# Enhance address extraction from transcript
def enhance_address_from_transcript(transcript, address):
    # First, look for explicit street patterns
    street_pattern = r'(\d+\s+(?:[NSEW]\s+)?[A-Za-z\s\-]+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Court|Ct|Lane|Ln|Way|Boulevard|Blvd|Circle|Cir|Place|Pl|Terrace|Ter|Trail|Tr|Highway|Hwy|Parkway|Pkwy))'
    street_matches = re.findall(street_pattern, transcript, re.IGNORECASE)
    
    # Then try a simpler pattern for street names without type
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
                return match.strip()
    
    # Without a house number, just use the first good match if any
    all_matches = street_matches + simple_matches
    if all_matches:
        return all_matches[0].strip()
    
    return None

def process_from_file(transcript_file):
    """Read transcript from file and process it."""
    try:
        with open(transcript_file, 'r') as f:
            transcript = f.read().strip()
        
        return process_transcript(transcript)
    
    except Exception as e:
        print(f"Error reading file {transcript_file}: {e}")
        return None

def process_interactive():
    """Process transcript entered by the user."""
    print("\nEnter emergency transcript (press Enter twice to process):")
    lines = []
    while True:
        line = input()
        if not line and lines:  # Empty line and we have content
            break
        lines.append(line)
    
    transcript = "\n".join(lines)
    return process_transcript(transcript)

def main():
    parser = argparse.ArgumentParser(description="Process audio transcript for emergency dispatch")
    parser.add_argument("--file", "-f", help="Path to transcript file to process")
    parser.add_argument("--text", "-t", help="Transcript text to process directly")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("AUDIO TRANSCRIPT + VALIDATION SYSTEM".center(70))
    print("="*70 + "\n")
    
    if args.file:
        print(f"Processing transcript from file: {args.file}")
        dispatch_report = process_from_file(args.file)
    elif args.text:
        print(f"Processing provided transcript")
        dispatch_report = process_transcript(args.text)
    else:
        print("No transcript file or text provided. Starting interactive mode.")
        dispatch_report = process_interactive()
    
    if dispatch_report:
        print("\nProcessing complete!")
    else:
        print("\nError processing transcript.")

if __name__ == "__main__":
    main() 
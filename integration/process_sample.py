#!/usr/bin/env python3
"""
This script processes the sample transcript with the ML interpretation layer.
It demonstrates how the system would interpret an emergency call in a real scenario.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def main():
    print("\n" + "="*70)
    print("SAMPLE TRANSCRIPT PROCESSING DEMONSTRATION".center(70))
    print("="*70 + "\n")
    
    # Get paths
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    transcript_path = os.path.join(current_dir, "audiotranscript copy", "sample_transcript.txt")
    
    # Check if the transcript exists
    if not os.path.exists(transcript_path):
        print(f"❌ Error: Sample transcript not found at {transcript_path}")
        return
    
    print(f"✅ Found sample transcript at: {transcript_path}")
    
    # Read the transcript
    with open(transcript_path, "r") as f:
        transcript_lines = f.readlines()
    
    # Filter for Speaker 2 lines only
    speaker2_lines = []
    for line in transcript_lines:
        if "Speaker 2" in line:
            # Get the index of the line with the text
            idx = transcript_lines.index(line)
            # Get the actual text (which is in the next line)
            if idx + 1 < len(transcript_lines):
                text = transcript_lines[idx + 1].strip()
                speaker2_lines.append(f"Speaker 2: {text}")
    
    if not speaker2_lines:
        print("\n❌ No Speaker 2 lines found in the transcript.")
        return
    
    print(f"\n📝 Found {len(speaker2_lines)} lines from Speaker 2 (the caller):")
    for i, line in enumerate(speaker2_lines):
        print(f"  {i+1}. {line}")
    
    # Process each line with the ML interpreter
    print("\n" + "-"*70)
    print("PROCESSING CALLER TRANSCRIPTS".center(70))
    print("-"*70)
    
    results = []
    
    for i, line in enumerate(speaker2_lines):
        print(f"\n🧠 Processing line {i+1}/{len(speaker2_lines)}: {line[:70]}...")
        
        # Run the ML interpreter
        try:
            # Create a command to run the interpreter
            interpreter_command = f"cd '{current_dir}' && source venv/bin/activate && python -c \"" \
                f"from main import AudioTranscriptInterpreter; " \
                f"interpreter = AudioTranscriptInterpreter(output_dir='interpretation_outputs'); " \
                f"result = interpreter.process_transcript('''{line}'''); " \
                f"print(repr(result)) if result else print('None')\""
            
            # Run the command
            output = subprocess.check_output(interpreter_command, shell=True, text=True)
            result_str = output.strip()
            
            # Parse the result
            if result_str and result_str != "None":
                # Convert string representation to dict
                try:
                    result_dict = eval(result_str)
                    results.append(result_dict)
                    
                    # Display the result
                    print("\n==================================================")
                    print("EMERGENCY CALL INTERPRETATION")
                    print("==================================================")
                    print(f"INCIDENT TYPE: {result_dict.get('incident_type', 'UNKNOWN').upper()}")
                    print(f"LOCATION: {result_dict.get('address', 'unknown address')}")
                    print(f"CASUALTIES: {result_dict.get('casualties', 'none')}")
                    
                    # If enhanced features were applied
                    if 'confidence' in result_dict:
                        print(f"CONFIDENCE: {result_dict.get('confidence', 0):.2f}")
                    
                    if 'address_validation' in result_dict:
                        addr_valid = result_dict.get('address_validation', {})
                        print(f"ADDRESS VALID: {addr_valid.get('valid', False)} (Confidence: {addr_valid.get('confidence', 0):.2f})")
                    
                    if 'casualties_structured' in result_dict:
                        cas = result_dict.get('casualties_structured', {})
                        affected = []
                        if cas.get('children', False): affected.append("Children")
                        if cas.get('elderly', False): affected.append("Elderly")
                        if cas.get('pets', False): affected.append("Pets")
                        if cas.get('caller', False): affected.append("Caller")
                        if affected:
                            print(f"AFFECTED: {', '.join(affected)}")
                    
                    if 'priority' in result_dict:
                        print(f"PRIORITY: {result_dict.get('priority_level', 'UNKNOWN')} ({result_dict.get('priority', 0):.1f})")
                    
                    print("==================================================\n")
                except Exception as e:
                    print(f"⚠️ Could not parse result: {result_str}")
                    print(f"⚠️ Error: {e}")
            else:
                print("⚠️ No result returned for this line.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running ML interpreter: {e}")
    
    # Save the results
    if results:
        os.makedirs(os.path.join(current_dir, "interpretation_outputs"), exist_ok=True)
        results_file = os.path.join(current_dir, "interpretation_outputs", f"sample_interpretations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Saved {len(results)} interpretations to {results_file}")
        
        # Run dispatcher router on the interpretations
        print("\n" + "-"*70)
        print("DISPATCHER ROUTING".center(70))
        print("-"*70)
        
        try:
            # Create a command to run the router
            router_command = f"cd '{current_dir}' && source venv/bin/activate && python -c \"" \
                f"from dispatcher_router import IncidentRouter; " \
                f"import json; " \
                f"router = IncidentRouter(); " \
                f"with open('{results_file}', 'r') as f: " \
                f"    interpretations = json.load(f); " \
                f"routing_results = [router.route(interp) for interp in interpretations]; " \
                f"print(json.dumps(routing_results, indent=2))\""
            
            # Run the command
            output = subprocess.check_output(router_command, shell=True, text=True)
            routing_results = json.loads(output.strip())
            
            # Display the routing results
            for i, result in enumerate(routing_results):
                print(f"\n🚨 Routing result for interpretation {i+1}:")
                print(f"  Status: {result.get('status', 'unknown')}")
                print(f"  Handler: {result.get('handler', 'unknown')}")
                print(f"  Message: {result.get('message', 'No message')}")
                print(f"  Resources dispatched:")
                for resource in result.get('resources', []):
                    print(f"    - {resource.replace('_', ' ').title()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running dispatcher router: {e}")
    else:
        print("\n❌ No valid interpretations were generated.")
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE".center(70))
    print("="*70 + "\n")

if __name__ == "__main__":
    main() 
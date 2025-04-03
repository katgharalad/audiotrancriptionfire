#!/usr/bin/env python3
import os
import sys
import json
import traceback
from interpreter import AudioTranscriptInterpreter

def test_integration():
    """
    Test the integration between AudioTranscriptInterpreter and 
    the AddressValidationEngine.
    """
    print("\n" + "="*70)
    print("AUDIOTRANSCRIPY + VALIDATION ENGINE INTEGRATION TEST".center(70))
    print("="*70 + "\n")
    
    # Create an output directory for test results
    output_dir = "test_validation_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Find the validation engine data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    validation_dir = os.path.join(project_root, "validationengine")
    
    try:
        # Initialize the interpreter with validation engine
        print(f"Initializing interpreter with validation data from: {validation_dir}")
        interpreter = AudioTranscriptInterpreter(
            output_dir=output_dir,
            validation_data_dir=validation_dir
        )
        
        # Test cases from validation engine test cases
        test_transcripts = [
            "Speaker 2: There is a fire at 162 MUIRWOOD VILLAGE DR.",
            "Speaker 2: I'm outside Muirwood Village Apts and it's burning.",
            "Speaker 2: Smoke coming from the building near Muirwood Village on MUIRWOOD VILLAGE DR.",
            "Speaker 2: I'm across the street from Muirwood Village Apts, something exploded.",
            "Speaker 2: There's something burning at 1000 Sunbury Rd.",
            "Speaker 2: Outside the Delaware City Police Department — send help.",
            "Speaker 2: Fire in the woods by the Stratford Ecological Center.",
            "Speaker 2: Explosion near the Kroger parking lot on North Houk Rd.",
            "Speaker 2: Caller reports flames behind Liberty Township Fire Station.",
            "Speaker 2: Kids trapped at Camp Lazarus. Structure fire.",
            "Speaker 2: Smoke at Glenross Golf Clubhouse.",
            "Speaker 2: Fire near Hayes High School football stadium!",
            "Speaker 2: Smoke coming from behind the Delaware County EMS Post."
        ]
        
        print("Processing test transcripts...\n")
        
        # Process each test transcript
        results = []
        for i, transcript in enumerate(test_transcripts):
            print(f"Test Case #{i+1}: \"{transcript}\"")
            print("-" * 50)
            
            try:
                # Process the transcript
                result = interpreter.process_transcript(transcript)
                
                if result:
                    results.append(result)
                    
                    # Print key validation results
                    print(f"Reverse Geocoded Address: {result.get('reverse_geocoded_address', 'Unknown')}")
                    print(f"Landmark: {result.get('landmark', 'None')}")
                    print(f"Address Confidence: {result.get('address_confidence', 0):.2f}")
                    print(f"Jurisdiction: {result.get('jurisdiction', 'Unknown')}")
                    print(f"ZIP Code: {result.get('matched_zip', 'Unknown')}")
                    needs_verification = result.get('needs_verification', True)
                    print(f"Needs Verification: {'Yes' if needs_verification else 'No'}")
                else:
                    print("No result returned")
            except Exception as e:
                print(f"Error processing transcript: {e}")
                traceback.print_exc()
                
            print("=" * 70 + "\n")
        
        # Save all results to a file
        with open(f"{output_dir}/integration_test_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"All results saved to {output_dir}/integration_test_results.json")
        print(f"Total of {len(results)} interpretations were processed")
        
        # Print success metrics
        if results:
            valid_addresses = sum(1 for r in results if r.get('address_confidence', 0) > 0.7)
            landmarks_found = sum(1 for r in results if r.get('landmark'))
            
            print("\nSuccess Metrics:")
            print(f"Valid Addresses: {valid_addresses}/{len(results)} ({valid_addresses/len(results)*100:.1f}%)")
            print(f"Landmarks Found: {landmarks_found}/{len(results)} ({landmarks_found/len(results)*100:.1f}%)")
        else:
            print("\nNo successful interpretations to generate metrics.")
        
        print("\nIntegration test completed!")
        
    except Exception as e:
        print(f"Error during integration test: {e}")
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    if test_integration():
        sys.exit(0)
    else:
        sys.exit(1) 
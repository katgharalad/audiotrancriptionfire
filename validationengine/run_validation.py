#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import json

def run_validation_engine(transcript=None):
    """
    Runs the validation engine using the virtual environment.
    
    Args:
        transcript (str, optional): Text to validate. If None, user will be prompted.
    """
    print("\n" + "="*70)
    print("VALIDATION ENGINE TEST".center(70))
    print("="*70 + "\n")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define venv path
    venv_dir = os.path.join(script_dir, "venv")
    
    # Check if venv exists
    if not os.path.exists(venv_dir):
        print("Virtual environment not found. Setting up now...")
        setup_script = os.path.join(script_dir, "setup_venv.py")
        
        # Create setup script if it doesn't exist
        if not os.path.exists(setup_script):
            print("Setup script not found. Please run setup_venv.py first.")
            return False
        
        # Run setup script
        try:
            subprocess.run([sys.executable, setup_script], check=True)
        except subprocess.CalledProcessError:
            print("Failed to set up virtual environment.")
            return False
    
    # Get transcript to validate
    if transcript is None:
        print("Enter a transcript to validate (or press Enter to use a demo transcript):")
        transcript = input("> ").strip()
        
        if not transcript:
            transcript = "Speaker 2: There's a fire at Smith Elementary School."
            print(f"Using demo transcript: '{transcript}'")
    
    # Determine python path based on OS
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, "Scripts", "python")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
    
    # Create a temporary script to run the validation
    temp_script = os.path.join(script_dir, "_temp_validation.py")
    with open(temp_script, "w") as f:
        f.write("""
from validation_engine_v2 import AddressValidationEngine
import json
import sys

# Initialize the engine
engine = AddressValidationEngine()

# Get the transcript
transcript = sys.argv[1]

# Generate validation report
result = engine.generate_validation_report(transcript)

# Print the result as JSON
print(json.dumps(result, indent=2))
""")
    
    try:
        # Run the validation
        print("\nRunning validation engine...")
        result = subprocess.run(
            [python_path, temp_script, transcript],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse and display the result
        try:
            validation_result = json.loads(result.stdout)
            
            print("\nVALIDATION RESULTS:")
            print("=" * 50)
            print(f"Address Validity: {validation_result.get('address_validity', False)}")
            print(f"Matched Address: {validation_result.get('matched_address', 'Unknown')}")
            print(f"Matched Landmark: {validation_result.get('matched_landmark', 'None')}")
            print(f"Confidence Score: {validation_result.get('confidence_score', 0):.2f}")
            print(f"ZIP Code: {validation_result.get('zip_code', 'Unknown')}")
            print(f"Jurisdiction: {validation_result.get('jurisdiction', 'Unknown')}")
            print(f"Needs Verification: {validation_result.get('needs_verification', True)}")
            if 'processing_time_ms' in validation_result:
                print(f"Processing Time: {validation_result.get('processing_time_ms')} ms")
        except json.JSONDecodeError:
            print("\nERROR: Could not parse result as JSON.")
            print("Raw output:")
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Validation failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        return False
    finally:
        # Clean up temporary script
        if os.path.exists(temp_script):
            os.remove(temp_script)
    
    return True

if __name__ == "__main__":
    # Get transcript from command line if provided
    transcript = None
    if len(sys.argv) > 1:
        transcript = " ".join(sys.argv[1:])
    
    # Run the validation
    if run_validation_engine(transcript):
        print("\nValidation completed successfully!")
    else:
        print("\nValidation failed. Please check the errors above.")
        sys.exit(1) 
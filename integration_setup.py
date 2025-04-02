#!/usr/bin/env python3
"""
This script helps set up the integration between AudioTranscripY and the ML Interpretation Layer.
It checks dependencies, verifies installations, and provides guidance on how to run the integrated system.
"""

import os
import sys
import subprocess
import importlib
import json
from pathlib import Path

def check_command(command):
    """Check if a command is available in the system."""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_importable(module_name):
    """Check if a Python module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    print("\n" + "="*70)
    print("AUDIOTRANSCRIPY + ML INTERPRETATION LAYER INTEGRATION SETUP".center(70))
    print("="*70 + "\n")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Using Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Error: Python 3.8+ is required.")
        return
    else:
        print("✅ Python version check passed!")
    
    # Check current directory
    current_dir = Path(os.getcwd())
    print(f"\nCurrent directory: {current_dir}")
    
    # Check for AudioTranscripY folder
    audiotranscript_dir = current_dir / "audiotranscript copy"
    if not audiotranscript_dir.exists():
        print("❌ Error: 'audiotranscript copy' directory not found.")
        print("Make sure you have the AudioTranscripY system in this directory.")
        return
    else:
        print(f"✅ AudioTranscripY found at: {audiotranscript_dir}")
    
    # Check for ML models
    ml_models_files = [
        current_dir / "incident_model.pkl",
        current_dir / "casualties_model.pkl"
    ]
    
    ml_models_exist = all(f.exists() for f in ml_models_files)
    if not ml_models_exist:
        print("\n❌ ML models not found. Have you trained the models?")
        print("Run 'python model_training.py' first.")
    else:
        print("✅ ML models found and ready!")
    
    # Check for AudioTranscripY virtual environment
    whisper_env = audiotranscript_dir / "whisper_env"
    if whisper_env.exists():
        print(f"\n✅ AudioTranscripY virtual environment found at: {whisper_env}")
    else:
        print("\n❌ AudioTranscripY virtual environment not found.")
        print("You may need to set up the virtual environment for AudioTranscripY.")
    
    # Check for main ML environment
    ml_env = current_dir / "venv"
    if ml_env.exists():
        print(f"✅ ML interpretation layer virtual environment found at: {ml_env}")
    else:
        print("⚠️ ML interpretation layer virtual environment not found.")
        print("Consider creating a virtual environment for the ML components.")
    
    # Prepare integration instructions
    print("\n" + "="*70)
    print("INTEGRATION INSTRUCTIONS".center(70))
    print("="*70)
    
    # Create integration directory
    integration_dir = current_dir / "integration"
    integration_dir.mkdir(exist_ok=True)
    
    # Create integration script - using triple quotes with raw strings to avoid issues
    integration_script = r'''#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from datetime import datetime

def run_transcription():
    """Run AudioTranscripY in a separate process and capture its output."""
    print("\n📣 Starting AudioTranscripY...")
    audiotranscript_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audiotranscript copy")
    
    # Activate AudioTranscripY's environment and run it
    transcript_file = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    command = f"cd '{audiotranscript_dir}' && source whisper_env/bin/activate && python main.py"
    
    print("\nRunning command:", command)
    print("\n⚠️ Important: When running AudioTranscripY, press ENTER to stop recording.")
    print("After stopping, the transcript will be processed by the ML interpretation layer.\n")
    
    # Run the command (this will block until AudioTranscripY completes)
    subprocess.run(command, shell=True)
    
    # Find the most recent transcript file
    transcript_files = [f for f in os.listdir(audiotranscript_dir) 
                       if f.startswith("transcript_") and f.endswith(".txt")]
    
    if not transcript_files:
        print("\n❌ No transcript files found. AudioTranscripY may not have completed successfully.")
        return None
    
    # Get the most recent transcript file
    transcript_file = max(transcript_files, key=lambda f: os.path.getmtime(os.path.join(audiotranscript_dir, f)))
    transcript_path = os.path.join(audiotranscript_dir, transcript_file)
    
    print(f"\n✅ Found transcript file: {transcript_file}")
    return transcript_path

def process_transcript(transcript_path):
    """Process the transcript with the ML interpretation layer."""
    if not transcript_path or not os.path.exists(transcript_path):
        print("\n❌ No valid transcript file to process.")
        return
    
    print("\n🧠 Processing transcript with ML interpretation layer...")
    
    # Read the transcript
    with open(transcript_path, "r") as f:
        transcript_lines = f.readlines()
    
    # Filter for Speaker 2 lines only
    speaker2_lines = [line.strip() for line in transcript_lines if "Speaker 2:" in line]
    
    if not speaker2_lines:
        print("\n⚠️ No Speaker 2 lines found in the transcript. Nothing to interpret.")
        return
    
    print(f"\n📝 Found {len(speaker2_lines)} lines from Speaker 2 (the caller).")
    
    # Prepare to run the ML interpreter on each line
    ml_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Activate the ML environment and run the interpreter for each line
    results = []
    
    for i, line in enumerate(speaker2_lines):
        print(f"\nProcessing line {i+1}/{len(speaker2_lines)}: {line[:50]}...")
        
        # Save the line to a temporary file
        temp_file = os.path.join(ml_dir, "integration", "temp_transcript.txt")
        with open(temp_file, "w") as f:
            f.write(line)
        
        # Run the ML interpreter
        command = f"cd '{ml_dir}' && source venv/bin/activate && python -c 'from main import AudioTranscriptInterpreter; interpreter = AudioTranscriptInterpreter(); result = interpreter.process_transcript(\"{line}\"); print(result)'"
        
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            result = output.strip()
            
            if result:
                try:
                    # Convert string representation of dict to actual dict
                    result_dict = eval(result)
                    results.append(result_dict)
                except:
                    print(f"\n⚠️ Could not parse result: {result}")
            else:
                print("\n⚠️ No result returned for this line.")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running ML interpreter: {e}")
    
    # Save the results
    if results:
        results_file = os.path.join(ml_dir, "integration", f"interpretations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Saved {len(results)} interpretations to {results_file}")
        print("\n📊 Sample interpretation:")
        print(json.dumps(results[0], indent=2))
    else:
        print("\n❌ No valid interpretations were generated.")

def main():
    print("\n" + "="*70)
    print("AUDIOTRANSCRIPY + ML INTERPRETATION LAYER INTEGRATION".center(70))
    print("="*70 + "\n")
    
    print("This script will:") 
    print("1. Run AudioTranscripY to capture and transcribe audio")
    print("2. Process the resulting transcript with the ML interpretation layer")
    print("3. Save the interpretations to a JSON file")
    
    input("\nPress ENTER to begin...")
    
    # Run AudioTranscripY
    transcript_path = run_transcription()
    
    # Process the transcript
    if transcript_path:
        process_transcript(transcript_path)
    
    print("\n" + "="*70)
    print("INTEGRATION COMPLETE".center(70))
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
'''
    
    # Save the integration script
    with open(integration_dir / "run_integration.py", "w") as f:
        f.write(integration_script)
    
    # Make the script executable
    os.chmod(integration_dir / "run_integration.py", 0o755)
    
    print("\n✅ Created integration script at:", integration_dir / "run_integration.py")
    print("\nThis script provides a two-step process to run AudioTranscripY and then process")
    print("its output with the ML interpretation layer.")
    
    # Provide final instructions
    print("\n" + "-"*70)
    print("HOW TO RUN THE INTEGRATED SYSTEM".center(70))
    print("-"*70)
    print("\n1. Make sure both virtual environments are set up:")
    print("   - AudioTranscripY environment: Run 'source audiotranscript\\ copy/whisper_env/bin/activate'")
    print("   - ML environment: Run 'source venv/bin/activate'")
    print("\n2. Train your ML models if not done already:")
    print("   - Run 'python model_training.py'")
    print("\n3. Run the integration script:")
    print("   - Run 'python integration/run_integration.py'")
    print("\n4. Follow the on-screen instructions:")
    print("   - The script will first run AudioTranscripY to capture and transcribe audio")
    print("   - After recording, it will process the transcript with the ML interpretation layer")
    print("   - The interpretations will be saved to a JSON file in the integration directory")
    
    print("\n" + "="*70)
    print("SETUP COMPLETE".center(70))
    print("="*70 + "\n")
    
    # Create a startup script
    startup_script = """#!/bin/bash
echo "Starting AudioTranscripY + ML Integration..."

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the integration script
python "$DIR/integration/run_integration.py"
"""
    
    with open(current_dir / "run_integration.sh", "w") as f:
        f.write(startup_script)
    
    # Make the script executable
    os.chmod(current_dir / "run_integration.sh", 0o755)
    
    print("✅ Created startup script at:", current_dir / "run_integration.sh")
    print("You can now run './run_integration.sh' to start the integrated system.")

if __name__ == "__main__":
    main() 
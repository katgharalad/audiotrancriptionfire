#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from datetime import datetime

def run_transcription():
    """Run AudioTranscripY in a separate process and capture its output."""
    print("\nStarting AudioTranscripY...")
    audiotranscript_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audiotranscript copy")
    
    # Activate AudioTranscripY's environment and run it
    transcript_file = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    command = f"cd '{audiotranscript_dir}' && source whisper_env/bin/activate && python main.py"
    
    print("\nRunning command:", command)
    print("\nImportant: When running AudioTranscripY, press ENTER to stop recording.")
    print("After stopping, the transcript will be processed by the ML interpretation layer.\n")
    
    # Run the command (this will block until AudioTranscripY completes)
    subprocess.run(command, shell=True)
    
    # Find the most recent transcript file
    transcript_files = [f for f in os.listdir(audiotranscript_dir) 
                       if f.startswith("transcript_") and f.endswith(".txt")]
    
    if not transcript_files:
        print("\nNo transcript files found. AudioTranscripY may not have completed successfully.")
        return None
    
    # Get the most recent transcript file
    transcript_file = max(transcript_files, key=lambda f: os.path.getmtime(os.path.join(audiotranscript_dir, f)))
    transcript_path = os.path.join(audiotranscript_dir, transcript_file)
    
    print(f"\nFound transcript file: {transcript_file}")
    return transcript_path

def process_transcript_with_whole_processor(transcript_path):
    """Process the transcript with the whole conversation processor."""
    if not transcript_path or not os.path.exists(transcript_path):
        print("\nNo valid transcript file to process.")
        return
    
    print("\nProcessing transcript with whole conversation processor...")
    
    # Run the whole conversation processor on the transcript
    ml_dir = os.path.dirname(os.path.dirname(__file__))
    processor_path = os.path.join(ml_dir, "integration", "whole_conversation_processor.py")
    
    # Make sure the processor is executable
    subprocess.run(f"chmod +x {processor_path}", shell=True, check=True)
    
    # Run the processor on the transcript
    command = f"{processor_path} '{transcript_path}'"
    
    print(f"\nRunning command: {command}")
    
    try:
        subprocess.run(command, shell=True, check=True)
        print("\nTranscript processing completed successfully.")
        
        # Find the most recent interpretation file
        interp_dir = os.path.join(ml_dir, "interpretation_outputs")
        interp_files = [f for f in os.listdir(interp_dir) 
                        if f.startswith("conversation_interpretation_") and f.endswith(".json")]
        
        if interp_files:
            # Get the most recent interpretation file
            interp_file = max(interp_files, key=lambda f: os.path.getmtime(os.path.join(interp_dir, f)))
            interp_path = os.path.join(interp_dir, interp_file)
            
            print(f"\nFound interpretation file: {interp_file}")
            
            # Display a summary of the interpretation
            with open(interp_path, "r") as f:
                interp_data = json.load(f)
            
            print("\nInterpretation Summary:")
            print("-" * 50)
            
            incident = interp_data.get("interpretation", {})
            routing = interp_data.get("routing", {})
            
            print(f"Incident Type: {incident.get('incident_type', 'unknown').upper()}")
            print(f"Location: {incident.get('address', 'unknown location')}")
            print(f"Casualties: {incident.get('casualties', 'none')}")
            
            if routing:
                print(f"\nRouting Status: {routing.get('status', 'unknown')}")
                print(f"Handler: {routing.get('handler', 'unknown')}")
                print(f"Resources: {', '.join([r.replace('_', ' ').title() for r in routing.get('resources', [])])}")
        else:
            print("\nNo interpretation files found.")
    
    except subprocess.CalledProcessError as e:
        print(f"\nError processing transcript: {e}")

def main():
    print("\n" + "="*70)
    print("AUDIOTRANSCRIPY + ML INTERPRETATION LAYER INTEGRATION".center(70))
    print("="*70 + "\n")
    
    print("This script will:") 
    print("1. Run AudioTranscripY to capture and transcribe audio")
    print("2. Process the resulting transcript with the whole conversation processor")
    print("3. Generate an incident interpretation and dispatcher routing")
    
    input("\nPress ENTER to begin...")
    
    # Run AudioTranscripY
    transcript_path = run_transcription()
    
    # Process the transcript with the whole conversation processor
    if transcript_path:
        process_transcript_with_whole_processor(transcript_path)
    
    print("\n" + "="*70)
    print("INTEGRATION COMPLETE".center(70))
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

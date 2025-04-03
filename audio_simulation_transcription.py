#!/usr/bin/env python3
import os
import sys
import time
import datetime
import json
import re
import subprocess
import argparse
import tempfile
import wave
import pyaudio
import numpy as np

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

# Check for venv
venv_dir = os.path.join(validation_dir, "venv")
venv_bin = os.path.join(venv_dir, "bin" if os.name != "nt" else "Scripts")
activate_script = os.path.join(venv_bin, "activate")

# Try to find the validation engine module
validation_module_path = os.path.join(validation_dir, "validation_engine_v2.py")
has_validation_module = os.path.exists(validation_module_path)
print(f"Validation engine module exists: {has_validation_module}")

# Try to find the ML interpretation module
ml_module_path = os.path.join(ml_dir, "interpreter.py")
has_ml_module = os.path.exists(ml_module_path)
print(f"ML interpretation module exists: {has_ml_module}")

# Create necessary directories
output_dir = os.path.join(script_dir, "live_outputs", "audio_simulation")
os.makedirs(output_dir, exist_ok=True)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 15  # Default recording time

def record_audio(filename, seconds=RECORD_SECONDS):
    """Record audio from microphone and save to a file."""
    p = pyaudio.PyAudio()
    
    print(f"\nRecording for {seconds} seconds...")
    print("Speak now!")
    
    # Open stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    
    # Start recording timer
    start_time = time.time()
    while time.time() - start_time < seconds:
        # Show progress bar
        elapsed = time.time() - start_time
        progress = min(elapsed / seconds, 1.0)
        bar_length = 40
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        remaining = seconds - elapsed
        sys.stdout.write(f'\rRecording: [{bar}] {elapsed:.1f}s/{seconds:.1f}s (remaining: {remaining:.1f}s)')
        sys.stdout.flush()
        
        # Record data
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("\nFinished recording!")
    
    # Stop and close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save to WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f"Audio saved to {filename}")
    return filename

def transcribe_with_whisper(audio_file):
    """Transcribe audio using Whisper."""
    print("\nTranscribing audio with Whisper...")
    
    try:
        # First try to use the OpenAI Whisper Python API
        try:
            import whisper
            print("Using OpenAI Whisper Python API...")
            
            # Load a small model to save time
            model = whisper.load_model("base")
            
            # Transcribe the audio
            result = model.transcribe(audio_file)
            transcript = result["text"]
            
            print(f"Transcription: {transcript}")
            return transcript
            
        except ImportError:
            print("OpenAI Whisper Python package not found, trying command line version...")
            
            # Try to use Whisper's command line tool as fallback
            try:
                result = subprocess.run(
                    ["whisper", audio_file, "--model", "base", "--language", "en"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Extract transcript from the output
                transcript = result.stdout.strip()
                
                # Also try to read the .txt file that Whisper creates
                txt_file = audio_file.replace(".wav", ".txt")
                if os.path.exists(txt_file):
                    with open(txt_file, 'r') as f:
                        transcript = f.read().strip()
                
                print(f"Transcription: {transcript}")
                return transcript
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Whisper command line tool not available: {e}")
                return None
                
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        import traceback
        traceback.print_exc()
        return None

def simulate_transcription():
    """Simulate transcription for testing the pipeline."""
    print("\n" + "="*70)
    print("SIMULATED AUDIO TRANSCRIPTION".center(70))
    print("="*70)
    
    print("\nPlease enter the transcript you want to simulate (as if it was spoken):")
    lines = []
    while True:
        line = input("> ")
        if not line:
            break
        lines.append(line)
    
    transcript = " ".join(lines)
    
    # Simulated processing delay
    print("\nSimulating audio processing...")
    for i in range(5):
        time.sleep(0.5)
        print(".", end="", flush=True)
    
    print(f"\n\nTranscription complete: {transcript}")
    return transcript

def process_transcript(transcript):
    """Process a transcript through validation and ML interpretation."""
    # Import validation and interpretation modules
    try:
        # Try the direct import first
        try:
            from validation_engine_v2 import AddressValidationEngine
            from ml_interpretation.interpreter import AudioTranscriptInterpreter
            
            print("Successfully imported validation and interpretation modules.")
        except ImportError as e:
            print(f"Error with direct import: {e}")
            
            # Try with explicit import paths
            print(f"Trying import with explicit paths...")
            validation_engine_path = os.path.join(validation_dir, "validation_engine_v2.py")
            ml_interpreter_path = os.path.join(ml_dir, "interpreter.py")
            
            if os.path.exists(validation_engine_path) and os.path.exists(ml_interpreter_path):
                # Try to import using importlib
                import importlib.util
                
                # Import validation engine
                spec = importlib.util.spec_from_file_location("validation_engine_v2", validation_engine_path)
                validation_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(validation_module)
                AddressValidationEngine = validation_module.AddressValidationEngine
                
                # Import ML interpreter
                spec = importlib.util.spec_from_file_location("interpreter", ml_interpreter_path)
                interpreter_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(interpreter_module)
                AudioTranscriptInterpreter = interpreter_module.AudioTranscriptInterpreter
                
                print("Successfully imported modules using importlib.")
            else:
                if not os.path.exists(validation_engine_path):
                    print(f"Validation engine file not found at: {validation_engine_path}")
                if not os.path.exists(ml_interpreter_path):
                    print(f"ML interpreter file not found at: {ml_interpreter_path}")
                raise ImportError("Could not find required module files.")
        
        # Initialize the modules
        validation_engine = AddressValidationEngine(data_dir=validation_dir)
        interpreter = AudioTranscriptInterpreter(output_dir=output_dir)
        
        print("Validation engine and ML interpretation modules loaded successfully.")
    except Exception as e:
        print(f"Error loading validation or interpretation modules: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to minimal processing without validation
        print("\n" + "="*70)
        print("WARNING: RUNNING WITHOUT VALIDATION ENGINE".center(70))
        print("="*70)
        
        class DummyValidationEngine:
            def generate_validation_report(self, text):
                print("Using dummy validation engine (validation module failed to load)")
                return {
                    "matched_address": "Unknown address - validation engine not available",
                    "confidence_score": 0.0,
                    "needs_verification": True
                }
        
        try:
            # Still try to load the interpreter
            from ml_interpretation.interpreter import AudioTranscriptInterpreter
            interpreter = AudioTranscriptInterpreter(output_dir=output_dir)
            validation_engine = DummyValidationEngine()
            print("Using ML interpreter with dummy validation engine.")
        except Exception as e2:
            print(f"Failed to load ML interpreter as fallback: {e2}")
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

def main():
    parser = argparse.ArgumentParser(description="Record, transcribe and process emergency calls")
    parser.add_argument("--seconds", "-s", type=int, default=RECORD_SECONDS,
                        help=f"Duration to record in seconds (default: {RECORD_SECONDS})")
    parser.add_argument("--audio", "-a", help="Path to existing audio file to process")
    parser.add_argument("--transcript", "-t", help="Path to existing transcript file to process")
    parser.add_argument("--simulate", action="store_true", help="Simulate audio transcription (type text instead of recording)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip address validation and only use ML interpretation")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("EMERGENCY CALL SIMULATION SYSTEM".center(70))
    print("="*70 + "\n")
    
    # If skip-validation was specified, modify the process_transcript function
    if args.skip_validation:
        global process_transcript
        original_process_transcript = process_transcript
        
        def process_transcript_no_validation(transcript):
            """Process a transcript with ML interpretation only (no validation)."""
            # Import interpretation module only
            try:
                from ml_interpretation.interpreter import AudioTranscriptInterpreter
                interpreter = AudioTranscriptInterpreter(output_dir=output_dir)
                print("ML interpretation module loaded successfully.")
            except Exception as e:
                print(f"Error loading ML interpretation module: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
            
            # Prepare transcript
            if "Speaker 2:" not in transcript:
                transcript_to_process = "Speaker 2: " + transcript
            else:
                transcript_to_process = transcript
            
            print("\n" + "="*70)
            print("PROCESSING TRANSCRIPT (NO VALIDATION)".center(70))
            print("="*70)
            print(f"Transcript: {transcript_to_process}")
            
            try:
                # Process interpretation
                print("\nGenerating interpretation...")
                interpretation = interpreter.process_transcript(transcript_to_process)
                
                # Generate and save report
                timestamp = int(time.time())
                report_file = os.path.join(output_dir, f"emergency_report_{timestamp}.json")
                
                # Create a dummy validation result
                validation_result = {
                    "matched_address": "Address validation skipped",
                    "confidence_score": 0.0,
                    "needs_verification": True
                }
                
                # Try to extract address from transcript using regex
                address = enhance_address_from_transcript(transcript_to_process, "Unknown address")
                if address:
                    validation_result["matched_address"] = address
                    validation_result["confidence_score"] = 0.5
                
                # Create dispatch report
                dispatch_report = {
                    "transcript": transcript_to_process,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "address": validation_result["matched_address"],
                    "landmark": None,
                    "zip_code": None,
                    "jurisdiction": None,
                    "incident_type": interpretation.get('incident_type', 'unknown'),
                    "priority": interpretation.get('priority', 3.0),
                    "needs_verification": True
                }
                
                with open(report_file, 'w') as f:
                    json.dump(dispatch_report, f, indent=2)
                
                # Print report
                print("\n" + "="*70)
                print("EMERGENCY DISPATCH REPORT".center(70))
                print("="*70)
                print(f"INCIDENT: {dispatch_report['incident_type'].upper()}")
                print(f"LOCATION: {address or 'Unknown address'}")
                print(f"PRIORITY: {dispatch_report['priority']}")
                print("STATUS: REQUIRES VERIFICATION")
                print("="*70)
                print(f"Report saved to: {report_file}")
                
                return dispatch_report
                
            except Exception as e:
                print(f"Error processing emergency: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # Replace the original function with our modified version
        process_transcript = process_transcript_no_validation
        print("Address validation has been disabled.")
    
    transcript = None
    
    if args.transcript:
        # Process existing transcript
        print(f"Processing transcript from: {args.transcript}")
        with open(args.transcript, 'r') as f:
            transcript = f.read().strip()
    
    elif args.audio:
        # Process existing audio file
        print(f"Processing audio from: {args.audio}")
        transcript = transcribe_with_whisper(args.audio)
        
        # Fallback to simulation if transcription failed
        if transcript is None:
            print("\nTranscription failed. Falling back to simulation mode.")
            transcript = simulate_transcription()
    
    elif args.simulate:
        # Simulate transcription
        print("Simulating audio transcription for emergency call")
        transcript = simulate_transcription()
    
    else:
        # Record and process new audio
        print("Starting new audio recording for emergency call simulation")
        
        # Create a temporary WAV file
        timestamp = int(time.time())
        audio_file = os.path.join(output_dir, f"emergency_audio_{timestamp}.wav")
        
        try:
            # Record audio
            record_audio(audio_file, seconds=args.seconds)
            
            # Transcribe audio
            transcript = transcribe_with_whisper(audio_file)
            
            # Fallback to simulation if transcription failed
            if transcript is None:
                print("\nTranscription failed. Falling back to simulation mode.")
                transcript = simulate_transcription()
                
        except Exception as e:
            print(f"\nError recording or transcribing audio: {e}")
            print("Falling back to simulation mode.")
            transcript = simulate_transcription()
    
    # Process transcript if we have one
    if transcript:
        dispatch_report = process_transcript(transcript)
        
        if dispatch_report:
            print("\nEmergency call processing complete!")
            
            # Show what would happen next in a real system
            print("\nIn a real system, this dispatch report would be sent to:")
            print("1. Emergency dispatch center")
            print("2. First responders' mobile devices")
            print("3. Incident management system")
            print("\nDispatch operators would verify the information and coordinate the response.")
        else:
            print("\nError processing emergency call.")
    else:
        print("\nNo transcript to process.")

if __name__ == "__main__":
    main() 
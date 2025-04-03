#!/usr/bin/env python3
import os
import sys
import time
import datetime
import sounddevice as sd
import numpy as np
import threading
import queue
from faster_whisper import WhisperModel
import json
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

# Create necessary directories
output_dir = os.path.join(script_dir, "live_outputs", "audio_transcription")
os.makedirs(output_dir, exist_ok=True)

# Global variables
transcript_buffer = queue.Queue()
audio_queue = queue.Queue()
is_running = True
current_transcript = ""
last_processed_time = 0
PROCESS_INTERVAL = 5  # Process transcript every 5 seconds
is_processing = False

# Initialize Whisper model
def initialize_whisper_model():
    print("Initializing Whisper model...")
    model_size = "base"  # Options: "tiny", "base", "small", "medium", "large"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return model

# Audio callback function to collect audio data
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata.copy())

# Process audio chunks with Whisper
def process_audio():
    global current_transcript, is_running, is_processing
    
    print("Starting audio processing thread...")
    model = initialize_whisper_model()
    
    while is_running:
        if audio_queue.qsize() > 0:
            # Collect audio chunks for 1 second
            audio_data = []
            chunks_to_process = min(10, audio_queue.qsize())  # Process at most 10 chunks
            
            for _ in range(chunks_to_process):
                if not audio_queue.empty():
                    audio_data.append(audio_queue.get())
            
            if audio_data:
                # Convert to the format expected by Whisper
                audio_array = np.concatenate(audio_data, axis=0)
                audio_array = audio_array.flatten().astype(np.float32)
                
                # Process with Whisper
                try:
                    segments, _ = model.transcribe(audio_array, beam_size=1, language="en")
                    
                    # Collect segments
                    segment_text = ""
                    for segment in segments:
                        segment_text += segment.text + " "
                    
                    if segment_text.strip():
                        # Append to transcript
                        current_transcript += segment_text
                        transcript_buffer.put(segment_text)
                        print(f"Transcript: {segment_text.strip()}")
                
                except Exception as e:
                    print(f"Error in transcription: {e}")
        
        # Sleep to avoid busy waiting
        time.sleep(0.1)

# Process transcript for emergency information
def process_transcript():
    global current_transcript, last_processed_time, is_running, is_processing
    
    print("Starting transcript processing thread...")
    
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
    
    while is_running:
        current_time = time.time()
        
        # Process transcript at intervals if it contains emergency indicators
        if current_time - last_processed_time > PROCESS_INTERVAL and not is_processing:
            # Check if transcript contains an emergency call
            if "Speaker 2:" in current_transcript or is_emergency_call(current_transcript):
                is_processing = True
                print("\n" + "="*70)
                print("EMERGENCY CALL DETECTED - PROCESSING".center(70))
                print("="*70)
                
                # Prepare transcript
                if "Speaker 2:" not in current_transcript:
                    transcript_to_process = "Speaker 2: " + current_transcript
                else:
                    transcript_to_process = current_transcript
                
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
                    
                    # Reset transcript
                    current_transcript = ""
                
                except Exception as e:
                    print(f"Error processing emergency: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Update last processed time
                last_processed_time = current_time
                is_processing = False
        
        # Sleep to avoid busy waiting
        time.sleep(0.5)

# Check if the transcript contains emergency indicators
def is_emergency_call(transcript):
    emergency_keywords = [
        "fire", "emergency", "accident", "crash", "help", "ambulance", 
        "burning", "explosion", "smoke", "gas leak", "injured", "trapped",
        "911", "medical", "collapsed", "disaster"
    ]
    
    text = transcript.lower()
    for keyword in emergency_keywords:
        if keyword in text:
            return True
    
    return False

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
    global is_running
    
    try:
        print("\n" + "="*70)
        print("AUDIO TRANSCRIPTION + VALIDATION SYSTEM".center(70))
        print("="*70 + "\n")
        
        print("Starting audio transcription and validation system...")
        print("This system will:")
        print("1. Continuously record and transcribe audio")
        print("2. Detect emergency calls")
        print("3. Validate addresses and generate dispatch reports")
        print("\nPress Ctrl+C to stop\n")
        
        # Set up audio input stream
        samplerate = 16000
        channels = 1
        
        # Start audio processing thread
        audio_thread = threading.Thread(target=process_audio)
        audio_thread.daemon = True
        audio_thread.start()
        
        # Start transcript processing thread
        transcript_thread = threading.Thread(target=process_transcript)
        transcript_thread.daemon = True
        transcript_thread.start()
        
        # Start recording with sounddevice
        with sd.InputStream(callback=audio_callback, channels=channels, samplerate=samplerate):
            print("Recording started. Speak into your microphone...\n")
            while True:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        is_running = False
        time.sleep(1)  # Give threads time to clean up
    
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        is_running = False
    
    print("System stopped.")

if __name__ == "__main__":
    main() 
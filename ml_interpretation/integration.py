import sys
import os
import time
import threading
import numpy as np
import queue
from threading import Thread
from datetime import datetime
import shutil

# Add the AudioTranscripY repository to the Python path
sys.path.append('./audiotrancriptionfire')

# Import from our ML interpretation layer
from main import AudioTranscriptInterpreter
from dispatcher_router import IncidentRouter

# Create a directory for outputs if it doesn't exist
os.makedirs("live_outputs", exist_ok=True)

def modify_audio_transcripy():
    """
    Create a modified version of the AudioTranscripY main.py file
    that exposes the necessary functionality for integration.
    """
    # Source and destination paths
    source_path = os.path.join('audiotrancriptionfire', 'main.py')
    dest_path = os.path.join('audiotrancriptionfire', 'integrated_main.py')
    
    # First make a copy of the original file
    shutil.copy2(source_path, dest_path)
    
    # Read the file content
    with open(dest_path, 'r') as f:
        content = f.readlines()
    
    # Find the main function
    main_line = -1
    for i, line in enumerate(content):
        if line.strip() == "def main():":
            main_line = i
            break
    
    if main_line == -1:
        print("Could not find main function in AudioTranscripY code.")
        return False
    
    # Add our integrated version of the main function
    integrated_main = """
def integrated_main(callback_func=None):
    \"\"\"
    Version of main() that accepts a callback function for new transcriptions.
    \"\"\"
    global stop_flag
    stop_flag = False
    
    print("\\n📝 Starting Integrated Real-Time Transcription with Speaker Detection")
    print("=======================================================")
    
    # Ask if user wants to select a specific input device
    print("\\nDo you want to select a specific input device? (y/n)")
    choice = input().strip().lower()
    
    device = None  # Default device
    if choice == 'y':
        devices = list_audio_devices()
        print("\\nEnter the device number you want to use:")
        device_id = int(input().strip())
        device = device_id
    
    # Buffer for collecting transcript entries
    transcript_buffer = []
    
    # Modified process_audio function that calls our callback
    def integrated_process_audio(transcript_buffer):
        \"\"\"Process audio with callback for ML layer.\"\"\"
        print("\\n🎤 Real-time transcription active - Speak now!")
        print("(Press ENTER to stop)\\n")
        
        accumulated_audio = np.array([], dtype=np.float32)
        last_print_time = time.time()
        current_text = ""
        last_speaker = None
        silence_duration = 0
        last_audio_time = time.time()
        is_speaking = False
        
        print("\\n" + "="*60)
        print("🔊 LIVE TRANSCRIPTION".center(60))
        print("="*60)
        
        while not stop_flag or not audio_queue.empty():
            try:
                # Get audio data from queue with timeout
                audio_data = audio_queue.get(timeout=0.3)  # Faster timeout
                
                # Check audio level
                audio_level = np.max(np.abs(audio_data))
                
                # Update speaking state
                was_speaking = is_speaking
                is_speaking = audio_level > MIN_AUDIO_LEVEL
                
                # Handle state change for visual feedback
                if is_speaking != was_speaking:
                    if is_speaking:
                        print("🎙️", end="", flush=True)
                        last_audio_time = time.time()
                        silence_duration = 0
                    else:
                        print(".", end="", flush=True)
                
                # Update silence duration if not speaking
                if not is_speaking:
                    silence_duration = time.time() - last_audio_time
                
                # Accumulate audio data
                accumulated_audio = np.append(accumulated_audio, audio_data)
                
                # Only process if we have enough audio data
                if len(accumulated_audio) >= BUFFER_SIZE:
                    # Identify speaker
                    speaker = speaker_manager.identify_speaker(accumulated_audio)
                    
                    # Transcribe audio (optimized settings)
                    segments, info = model.transcribe(
                        accumulated_audio,
                        beam_size=5,  # Reduced for speed
                        without_timestamps=True,
                        condition_on_previous_text=True,
                        language='en'
                    )
                    
                    # Process transcriptions
                    segments_list = list(segments)
                    
                    for segment in segments_list:
                        text = segment.text.strip()
                        if text:
                            # Clean up the text
                            text = remove_duplicates(text)
                            
                            # Adjust speaker change logic to prevent unnecessary resets
                            if (speaker != last_speaker or text.endswith(('.', '!', '?')) or 
                                len(current_text.split()) > 30 or silence_duration > 2.0):  # Reduced silence threshold
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                if current_text:
                                    if last_speaker:
                                        # Clean formatting for readability
                                        formatted_transcript = f"{last_speaker} [{timestamp}]: {current_text}"
                                        print(f"\\n\\n{formatted_transcript}")
                                        print("-" * 60)
                                        
                                        transcript_buffer.append({
                                            'timestamp': timestamp,
                                            'speaker': last_speaker,
                                            'text': current_text
                                        })
                                        
                                        # Call the callback function if provided
                                        if callback_func and last_speaker.startswith("Speaker 2"):
                                            callback_func(formatted_transcript)
                                    else:
                                        print(f"\\n\\nUnknown [{timestamp}]:")
                                        print(f"  {current_text}")
                                        print("-" * 60)
                                current_text = text
                                last_speaker = speaker
                            else:
                                if text not in current_text:
                                    current_text = f"{current_text} {text}"
                                    # Print updates without timestamp for continuations
                                    print(f"\\r  {current_text}", end="", flush=True)
                    
                    # Keep less overlap for faster processing
                    accumulated_audio = accumulated_audio[-BUFFER_SIZE//8:]
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\\nError in transcription: {e}", file=sys.stderr)
                continue
    
    # Start the processing thread with our integrated version
    processing_thread = threading.Thread(target=integrated_process_audio, args=(transcript_buffer,), daemon=True)
    processing_thread.start()
    
    # Start the input listening thread
    input_thread = threading.Thread(target=wait_for_exit, daemon=True)
    input_thread.start()
    
    try:
        # Start the audio stream with smaller blocksize
        with sd.InputStream(callback=callback,
                        channels=1,
                        samplerate=16000,
                        device=device,
                        blocksize=2000,  # Smaller chunks for faster updates
                        dtype=np.float32):
            print("\\nListening... (🎙️ = speaking, . = silence)")
            while not stop_flag:
                sd.sleep(100)
    except Exception as e:
        print(f"\\nError with audio stream: {e}", file=sys.stderr)
        stop_flag = True
    
    print("\\n🛑 Stopping recording...")
    processing_thread.join(timeout=2.0)
    
    # Save transcript if there's content
    if transcript_buffer:
        filename = save_transcript(transcript_buffer)
        print(f"✨ Transcription saved to {filename}")
    else:
        print("✨ Transcription completed (no content to save)")
"""
    
    # Insert our integrated_main function before the original main function
    content.insert(main_line, integrated_main)
    
    # Write the modified content back to the file
    with open(dest_path, 'w') as f:
        f.writelines(content)
    
    print(f"Created integrated version at {dest_path}")
    return True

def main():
    # Modify AudioTranscripY code to add our integration function
    if not modify_audio_transcripy():
        print("Failed to modify AudioTranscripY code.")
        return
    
    # Initialize our ML interpreter and router
    interpreter = AudioTranscriptInterpreter(output_dir="live_outputs")
    router = IncidentRouter()
    
    # Import from the modified AudioTranscripY
    try:
        sys.path.insert(0, os.path.abspath('./audiotrancriptionfire'))
        from integrated_main import integrated_main
    except ImportError as e:
        print(f"Failed to import from modified AudioTranscripY: {e}")
        return
    
    # Create transcript callback function
    transcript_queue = queue.Queue()
    
    def transcript_callback(transcript):
        """Callback function for new transcripts."""
        transcript_queue.put(transcript)
    
    # Start transcript processing thread
    def process_transcripts():
        processed_transcripts = set()
        
        while True:
            try:
                transcript = transcript_queue.get(timeout=1.0)
                
                if transcript and transcript not in processed_transcripts:
                    processed_transcripts.add(transcript)
                    
                    if transcript.startswith("Speaker 2:"):
                        print("\nProcessing caller transcript:")
                        print(transcript)
                        
                        # Process with our ML interpreter
                        result = interpreter.process_transcript(transcript)
                        print("\nInterpretation:")
                        print(result)
                        
                        # Route the incident
                        routing_result = router.route(result)
                        print("\nRouting result:")
                        print(routing_result)
                        print("\n" + "-"*50)
                        
                        # Save the results
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        result_file = os.path.join("live_outputs", f"incident_{timestamp}.json")
                        with open(result_file, 'w') as f:
                            import json
                            json.dump({
                                "transcript": transcript,
                                "interpretation": result,
                                "routing": routing_result
                            }, f, indent=2)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing transcript: {e}")
    
    # Start the transcript processing thread
    processing_thread = Thread(target=process_transcripts, daemon=True)
    processing_thread.start()
    
    # Start AudioTranscripY with our callback
    print("Starting integrated AudioTranscripY...")
    integrated_main(transcript_callback)

if __name__ == "__main__":
    main() 
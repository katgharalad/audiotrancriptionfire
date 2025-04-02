import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import sys
import threading
import queue
import time
from datetime import datetime
from sklearn.cluster import KMeans
import librosa
from collections import deque

def list_audio_devices():
    """List all available audio input devices."""
    print("\nAvailable audio input devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:  # Only show input devices
            print(f"{i}: {device['name']}")
    return devices

# Initialize audio processing queue
audio_queue = queue.Queue()

# Load the Whisper model - use tiny model for faster processing
try:
    print("\nLoading Whisper model (this may take a moment)...")
    model = WhisperModel('tiny', device='cpu', compute_type='float32')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    sys.exit(1)

stop_flag = False  # Flag to stop the recording

# Lower minimum audio level for better sensitivity
MIN_AUDIO_LEVEL = 0.00005  # Much lower threshold to detect quieter speech

# Use smaller buffer for faster processing
BUFFER_SIZE = 64000  # Reduced for faster transcription

class SpeakerManager:
    def __init__(self, num_speakers=2):
        self.num_speakers = num_speakers
        self.kmeans = KMeans(n_clusters=num_speakers, random_state=42)
        self.features_buffer = []
        self.initialized = False
        self.min_energy_threshold = 0.0005
        self.speaker_history = deque(maxlen=10)
        self.current_speaker = None
        self.last_switch_time = time.time()
        self.min_switch_interval = 0.5
        self.last_features = None
        
    def extract_features(self, audio_data):
        try:
            # Convert to float64 for librosa processing
            audio_data_64 = audio_data.astype(np.float64)
            
            # Extract fewer features for faster processing
            mfcc = librosa.feature.mfcc(y=audio_data_64, sr=16000, n_mfcc=13)
            
            # Calculate only mean for speed
            mfcc_mean = np.mean(mfcc, axis=1)
            
            # Use only MFCC features for speed
            self.last_features = mfcc_mean
            return mfcc_mean
        except Exception as e:
            return self.last_features
        
    def get_majority_speaker(self):
        """Get the most common speaker in recent history."""
        if not self.speaker_history:
            return None
        speakers = list(self.speaker_history)
        return max(set(speakers), key=speakers.count)
        
    def identify_speaker(self, audio_data):
        # Check energy
        energy = np.mean(audio_data ** 2)
        if energy < self.min_energy_threshold:
            return self.current_speaker or "Speaker Unknown"
        
        # Extract features
        features = self.extract_features(audio_data)
        if features is None:
            return self.current_speaker or "Speaker Unknown"
            
        # Add features to buffer
        self.features_buffer.append(features)
        if len(self.features_buffer) > 30:
            self.features_buffer = self.features_buffer[-30:]
        
        # Process features
        if len(self.features_buffer) >= 3:
            features_array = np.array(self.features_buffer)
            
            if not self.initialized:
                self.kmeans.fit(features_array)
                self.initialized = True
            
            # Predict speaker
            speaker_id = self.kmeans.predict([features])[0]
            predicted_speaker = f"Speaker {speaker_id + 1}"
            
            # Add to history
            self.speaker_history.append(predicted_speaker)
            
            # Get majority speaker
            majority_speaker = self.get_majority_speaker()
            
            # Update speaker if changed and enough time has passed
            current_time = time.time()
            if (majority_speaker != self.current_speaker and 
                (current_time - self.last_switch_time >= self.min_switch_interval)):
                self.current_speaker = majority_speaker
                self.last_switch_time = current_time
            
            return self.current_speaker or predicted_speaker
        
        return self.current_speaker or "Speaker Unknown"

# Initialize speaker manager
speaker_manager = SpeakerManager(num_speakers=2)

def remove_duplicates(text):
    """Remove repeated phrases and clean up text."""
    words = text.split()
    cleaned_words = []
    i = 0
    while i < len(words):
        if i + 2 < len(words) and ' '.join(words[i:i+2]) == ' '.join(words[i+2:i+4]):
            i += 2
        else:
            cleaned_words.append(words[i])
            i += 1
    return ' '.join(cleaned_words)

def callback(indata, frames, time, status):
    """Callback function for the audio stream."""
    if status:
        print(f"Status: {status}", file=sys.stderr, flush=True)
    
    # Convert input data to float32 and normalize
    audio_data = indata.copy()
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    
    # Normalize audio data
    audio_data = np.squeeze(audio_data)
    max_value = np.max(np.abs(audio_data))
    if max_value > 0:
        audio_data = audio_data / max_value
    
    # Put the audio data in the queue
    audio_queue.put(audio_data)

def process_audio(transcript_buffer):
    """Process audio data from the queue."""
    print("\n🎤 Real-time transcription active - Speak now!")
    print("(Press ENTER to stop)\n")
    
    accumulated_audio = np.array([], dtype=np.float32)
    last_print_time = time.time()
    current_text = ""
    last_speaker = None
    silence_duration = 0
    last_audio_time = time.time()
    is_speaking = False
    
    print("\n" + "="*60)
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
                                    print(f"\n\n{last_speaker} [{timestamp}]:")
                                    print(f"  {current_text}")
                                    print("-" * 60)
                                    
                                    transcript_buffer.append({
                                        'timestamp': timestamp,
                                        'speaker': last_speaker,
                                        'text': current_text
                                    })
                                else:
                                    print(f"\n\nUnknown [{timestamp}]:")
                                    print(f"  {current_text}")
                                    print("-" * 60)
                            current_text = text
                            last_speaker = speaker
                        else:
                            if text not in current_text:
                                current_text = f"{current_text} {text}"
                                # Print updates without timestamp for continuations
                                print(f"\r  {current_text}", end="", flush=True)
                
                # Keep less overlap for faster processing
                accumulated_audio = accumulated_audio[-BUFFER_SIZE//8:]
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"\nError in transcription: {e}", file=sys.stderr)
            continue

def save_transcript(transcript_buffer):
    """Save the transcript to a file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"transcript_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("TRANSCRIPTION\n")
        f.write("=" * 60 + "\n\n")
        
        for entry in transcript_buffer:
            f.write(f"{entry['speaker']} [{entry['timestamp']}]:\n")
            f.write(f"  {entry['text']}\n\n")
    
    return filename

def wait_for_exit():
    """Handle user input to stop recording."""
    global stop_flag
    input("")
    stop_flag = True

def main():
    global stop_flag
    
    print("\n📝 Starting Real-Time Transcription with Speaker Detection")
    print("=======================================================")
    
    # Ask if user wants to select a specific input device
    print("\nDo you want to select a specific input device? (y/n)")
    choice = input().strip().lower()
    
    device = None  # Default device
    if choice == 'y':
        devices = list_audio_devices()
        print("\nEnter the device number you want to use:")
        device_id = int(input().strip())
        device = device_id
    
    # Buffer for collecting transcript entries
    transcript_buffer = []
    
    # Start the processing thread
    processing_thread = threading.Thread(target=process_audio, args=(transcript_buffer,), daemon=True)
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
            print("\nListening... (🎙️ = speaking, . = silence)")
            while not stop_flag:
                sd.sleep(100)
    except Exception as e:
        print(f"\nError with audio stream: {e}", file=sys.stderr)
        stop_flag = True
    
    print("\n🛑 Stopping recording...")
    processing_thread.join(timeout=2.0)
    
    # Save transcript if there's content
    if transcript_buffer:
        filename = save_transcript(transcript_buffer)
        print(f"✨ Transcription saved to {filename}")
    else:
        print("✨ Transcription completed (no content to save)")

if __name__ == "__main__":
    main()
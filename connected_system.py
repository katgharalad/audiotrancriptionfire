import sys
import os
import threading
import time
from datetime import datetime
import json
import queue

# Add path to ensure access to both components
audio_transcript_path = os.path.join(os.path.dirname(__file__), "audiotranscript copy")
sys.path.append(audio_transcript_path)

# Import AudioTranscripY components - we need to handle the space in the folder name
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(audio_transcript_path, "main.py"))
audio_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio_module)

# Get components from the audio module
model = audio_module.model
list_audio_devices = audio_module.list_audio_devices
callback = audio_module.callback
audio_queue = audio_module.audio_queue
stop_flag = audio_module.stop_flag
SpeakerManager = audio_module.SpeakerManager
BUFFER_SIZE = audio_module.BUFFER_SIZE

import sounddevice as sd
import numpy as np

# Import ML interpretation components
from main import AudioTranscriptInterpreter
from dispatcher_router import IncidentRouter
from enhanced_features import (
    calculate_confidence_score, validate_address,
    predict_priority, structure_casualties
)

class ConnectedSystem:
    def __init__(self, output_dir="system_outputs"):
        """Initialize the connected system."""
        # Set up paths
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.speaker_manager = SpeakerManager(num_speakers=2)
        self.interpreter = AudioTranscriptInterpreter(output_dir=os.path.join(output_dir, "interpretations"))
        self.router = IncidentRouter()
        
        # Set up the default handlers
        self.setup_handlers()
        
        # Initialize state variables
        self.transcript_buffer = []
        self.is_running = False
        self.last_processing_time = time.time()
        self.processing_interval = 2.0  # Process every 2 seconds
        self.current_incident = None
        self.incidents = []
        
        print("Connected system initialized successfully!")
    
    def setup_handlers(self):
        """Set up handlers for different incident types in the router."""
        # Register handlers for different incident types
        @self.router.register_handler("kitchen_fire")
        def handle_kitchen_fire(interpretation):
            resources = ["fire_engine", "ambulance"]
            return {
                "message": "Dispatching fire units to kitchen fire",
                "resources": resources
            }
            
        @self.router.register_handler("structure_fire")
        def handle_structure_fire(interpretation):
            resources = ["fire_engine", "ladder_truck", "ambulance", "battalion_chief"]
            return {
                "message": "Dispatching fire units to structure fire",
                "resources": resources
            }
            
        @self.router.register_handler("gas_leak")
        def handle_gas_leak(interpretation):
            resources = ["fire_engine", "hazmat_unit", "utility_company"]
            return {
                "message": "Dispatching hazmat team to gas leak",
                "resources": resources
            }
            
        @self.router.register_handler("vehicle_fire")
        def handle_vehicle_fire(interpretation):
            resources = ["fire_engine"]
            return {
                "message": "Dispatching fire unit to vehicle fire",
                "resources": resources
            }
            
        @self.router.register_handler("wildfire")
        def handle_wildfire(interpretation):
            resources = ["brush_units", "water_tenders", "air_support", "mutual_aid"]
            return {
                "message": "Dispatching wildland fire units",
                "resources": resources
            }
    
    def process_audio_thread(self):
        """Process audio data from the queue in a separate thread."""
        print("\n🎤 Real-time transcription and interpretation active!")
        print("(Press ENTER to stop)\n")
        
        accumulated_audio = np.array([], dtype=np.float32)
        last_speaker = None
        current_text = ""
        
        print("\n" + "="*60)
        print("🔊 LIVE TRANSCRIPTION & INTERPRETATION".center(60))
        print("="*60)
        
        while self.is_running or not audio_queue.empty():
            try:
                # Get audio data from queue with timeout
                audio_data = audio_queue.get(timeout=0.3)
                
                # Accumulate audio data
                accumulated_audio = np.append(accumulated_audio, audio_data)
                
                # Only process if we have enough audio data
                if len(accumulated_audio) >= BUFFER_SIZE:
                    # Identify speaker
                    speaker = self.speaker_manager.identify_speaker(accumulated_audio)
                    
                    # Transcribe audio
                    segments, info = model.transcribe(
                        accumulated_audio,
                        beam_size=5,
                        without_timestamps=True,
                        condition_on_previous_text=True,
                        language='en'
                    )
                    
                    # Process transcriptions
                    segments_list = list(segments)
                    
                    for segment in segments_list:
                        text = segment.text.strip()
                        if text:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            
                            # Complete processing when speaker changes or at end of sentence
                            if speaker != last_speaker or text.endswith(('.', '!', '?')):
                                if current_text:
                                    if last_speaker:
                                        # Format transcript
                                        formatted_text = f"{last_speaker}: {current_text}"
                                        print(f"\n\n{formatted_text}")
                                        print("-" * 60)
                                        
                                        # Add to transcript buffer
                                        self.transcript_buffer.append({
                                            'timestamp': timestamp,
                                            'speaker': last_speaker,
                                            'text': current_text
                                        })
                                        
                                        # If this is Speaker 2 (the caller), process through ML interpretation
                                        if last_speaker == "Speaker 2" and len(current_text) > 10:
                                            self.process_caller_transcript(formatted_text, timestamp)
                                
                                current_text = text
                                last_speaker = speaker
                            else:
                                current_text += " " + text
                                
                    # Reset accumulated audio
                    accumulated_audio = np.array([], dtype=np.float32)
                
                # Process buffered transcripts periodically
                current_time = time.time()
                if current_time - self.last_processing_time >= self.processing_interval:
                    self.save_transcript()
                    self.last_processing_time = current_time
                
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error in audio processing: {e}")
                
        # Final save when thread stops
        self.save_transcript()
    
    def process_caller_transcript(self, transcript, timestamp):
        """Process a transcript from the caller (Speaker 2) through ML interpretation."""
        try:
            # Process through interpreter
            interpretation = self.interpreter.process_transcript(transcript)
            
            if interpretation:
                # Apply enhanced features
                confidence = calculate_confidence_score(interpretation)
                address_validation = validate_address(interpretation.get('address', ''))
                priority = predict_priority(
                    interpretation.get('incident_type', ''), 
                    interpretation.get('casualties', '')
                )
                structured_casualties = structure_casualties(interpretation.get('casualties', ''))
                
                # Add enhanced features to interpretation
                interpretation['confidence'] = confidence
                interpretation['address_validation'] = address_validation
                interpretation['priority'] = priority[0] if isinstance(priority, tuple) else priority
                interpretation['priority_level'] = priority[1] if isinstance(priority, tuple) else "UNKNOWN"
                interpretation['casualties_structured'] = structured_casualties
                interpretation['timestamp'] = timestamp
                
                # Route the interpretation
                routing_result = self.router.route(interpretation)
                
                # Update current incident
                self.current_incident = {
                    **interpretation,
                    "routing": routing_result
                }
                
                # Add to incidents list
                self.incidents.append(self.current_incident)
                
                # Display the interpretation and routing
                self.display_incident(self.current_incident)
                
                # Save incidents to file
                self.save_incidents()
        except Exception as e:
            print(f"Error processing transcript: {e}")
    
    def display_incident(self, incident):
        """Display incident information."""
        print("\n" + "="*50)
        print("🚨 EMERGENCY CALL INTERPRETATION 🚨")
        print("="*50)
        print(f"INCIDENT TYPE: {incident.get('incident_type', 'UNKNOWN').upper()}")
        print(f"CONFIDENCE: {incident.get('confidence', 0):.2f}")
        print(f"LOCATION: {incident.get('address', 'unknown address')}")
        
        # Address validation
        address_validation = incident.get('address_validation', {})
        print(f"ADDRESS VALID: {address_validation.get('valid', False)} (Confidence: {address_validation.get('confidence', 0):.2f})")
        
        # Casualties
        print(f"CASUALTIES: {incident.get('casualties', 'none')}")
        
        # Structured casualties
        casualties = incident.get('casualties_structured', {})
        affected = []
        if casualties.get('children', False): affected.append("Children")
        if casualties.get('elderly', False): affected.append("Elderly")
        if casualties.get('pets', False): affected.append("Pets")  
        if casualties.get('caller', False): affected.append("Caller")
        if affected:
            print(f"AFFECTED: {', '.join(affected)}")
        
        # Priority
        print(f"PRIORITY: {incident.get('priority_level', 'UNKNOWN')} ({incident.get('priority', 0):.1f})")
        
        # Resources being dispatched
        routing = incident.get('routing', {})
        if routing and 'resources' in routing:
            print("\nDISPATCHING:")
            for resource in routing.get('resources', []):
                print(f"- {resource.replace('_', ' ').title()}")
        
        print("="*50)
    
    def save_transcript(self):
        """Save the current transcript buffer to a file."""
        if self.transcript_buffer:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f"transcript_{timestamp}.txt")
            
            with open(filename, 'w') as f:
                for entry in self.transcript_buffer:
                    f.write(f"[{entry['timestamp']}] {entry['speaker']}: {entry['text']}\n")
            
            print(f"\nTranscript saved to {filename}")
    
    def save_incidents(self):
        """Save all incidents to a JSON file."""
        if self.incidents:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f"incidents_{timestamp}.json")
            
            with open(filename, 'w') as f:
                json.dump(self.incidents, f, indent=2)
    
    def run(self):
        """Run the connected system."""
        try:
            # List audio devices
            devices = list_audio_devices()
            
            # Ask for device selection
            device_idx = input("\nSelect input device number (default: 0): ")
            if device_idx.strip() == "":
                device_idx = 0
            else:
                device_idx = int(device_idx)
            
            # Set the flag to running
            self.is_running = True
            global stop_flag
            stop_flag = False
            
            # Start the audio processing thread
            proc_thread = threading.Thread(target=self.process_audio_thread)
            proc_thread.start()
            
            # Start the audio stream
            with sd.InputStream(callback=callback, 
                             device=device_idx,
                             channels=1,
                             samplerate=16000,
                             blocksize=8000):
                print("\nRecording started. Press Enter to stop...")
                input()  # Wait for Enter key to stop
                
                # Set the stop flag
                self.is_running = False
                stop_flag = True
            
            # Wait for processing thread to finish
            proc_thread.join()
            
            print("\nRecording and processing stopped.")
            print(f"Saved output to {self.output_dir}")
            
        except Exception as e:
            print(f"Error: {e}")
            self.is_running = False
            stop_flag = True

if __name__ == "__main__":
    # Create and run the connected system
    system = ConnectedSystem()
    system.run() 
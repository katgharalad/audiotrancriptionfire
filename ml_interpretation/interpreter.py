import os
import json
import datetime
import sys
import importlib.util

# More robust path handling for validation engine
validationengine_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'validationengine')

# Add validationengine to the path
if validationengine_path not in sys.path:
    sys.path.insert(0, validationengine_path)

# Import validation engine with error handling
try:
    from validation_engine_v2 import AddressValidationEngine
    validation_engine_available = True
except ImportError:
    print("Warning: Could not import validation engine. Will run without address validation.")
    validation_engine_available = False

class AudioTranscriptInterpreter:
    """
    Integration layer that processes transcripts from AudioTranscripY
    and interprets them using the trained ML models with address validation.
    """
    def __init__(self, output_dir="interpretations", verification_threshold=0.7, validation_data_dir=None):
        """
        Initialize the interpreter with both ML models and validation engine.
        
        Args:
            output_dir (str): Directory to save interpretations
            verification_threshold (float): Confidence threshold for verification
            validation_data_dir (str, optional): Directory containing validation data files
        """
        self.output_dir = output_dir
        self.verification_threshold = verification_threshold
        self.verification_queue = []
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create verification directory if it doesn't exist
        verification_dir = f"{output_dir}/needs_verification"
        if not os.path.exists(verification_dir):
            os.makedirs(verification_dir)
        
        # Initialize existing models
        self.incident_model = None  # This would be loaded from trained models
        self.casualty_model = None  # This would be loaded from trained models
        
        # Initialize the validation engine
        if validation_engine_available:
            try:
                # Use validation data dir if provided, otherwise use default path
                data_dir = validation_data_dir if validation_data_dir else validationengine_path
                self.validator = AddressValidationEngine(data_dir=data_dir)
                self.validation_enabled = True
                print(f"Validation engine initialized with data directory: {data_dir}")
            except Exception as e:
                print(f"Error initializing validation engine: {e}")
                print("Running without address validation.")
                self.validation_enabled = False
        else:
            self.validation_enabled = False
        
        self.current_session = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.interpretation_log = []
        
        print(f"AudioTranscriptInterpreter initialized. Output directory: {output_dir}")
        print("Ready to process transcripts. Waiting for input...")
    
    def process_transcript(self, transcript: str):
        """
        Process a single transcript and return the interpretation with validation.
        Only processes transcripts from Speaker 2 (the caller).
        
        Args:
            transcript (str): Raw transcript text
            
        Returns:
            dict: Interpretation result or None if not from Speaker 2
        """
        # Only process if the transcript is from Speaker 2 (the caller)
        if not transcript.startswith("Speaker 2:"):
            print("Ignored transcript (not from caller)")
            return None
        
        # Use the trained models to interpret the transcript for incident and casualty info
        # This would be the existing ML interpretation code
        result = self._interpret_with_ml(transcript)
        
        if result:
            # Add validation if available
            if self.validation_enabled:
                try:
                    # Get validation results from the validation engine
                    validation_result = self.validator.generate_validation_report(transcript)
                    
                    # Merge validation results into the main result dictionary
                    result.update({
                        "reverse_geocoded_address": validation_result.get("matched_address"),
                        "landmark": validation_result.get("matched_landmark"),
                        "address_confidence": validation_result.get("confidence_score"),
                        "matched_zip": validation_result.get("zip_code"),
                        "jurisdiction": validation_result.get("jurisdiction"),
                        "needs_verification": validation_result.get("needs_verification", False)
                    })
                except Exception as e:
                    print(f"Error during address validation: {e}")
                    print("Continuing without address validation for this transcript.")
                    # Add default values
                    result.update({
                        "reverse_geocoded_address": result.get("address", "Unknown address"),
                        "landmark": None,
                        "address_confidence": 0.0,
                        "matched_zip": None,
                        "jurisdiction": None,
                        "needs_verification": True
                    })
            else:
                # Add default values if validation is not available
                result.update({
                    "reverse_geocoded_address": result.get("address", "Unknown address"),
                    "landmark": None,
                    "address_confidence": 0.0,
                    "matched_zip": None,
                    "jurisdiction": None,
                    "needs_verification": True
                })
            
            # Add timestamp
            result['timestamp'] = datetime.datetime.now().isoformat()
            result['transcript'] = transcript
            
            # Log the interpretation
            self.interpretation_log.append(result)
            
            # Save to file
            self._save_interpretation(result)
            
            # Check if needs verification
            if result.get('needs_verification', False):
                self._add_to_verification_queue(result)
            
            # Print a formatted version of the result
            self._print_interpretation(result)
            
        return result
    
    def _interpret_with_ml(self, transcript_text):
        """
        Use ML models to interpret incident type and casualties.
        This is a placeholder for the existing ML interpretation code.
        
        Args:
            transcript_text (str): Raw transcript text
            
        Returns:
            dict: Basic interpretation result
        """
        # This is where you would call your existing ML models
        # For now, return a mock result
        return {
            "incident_type": "structure fire",  # This would come from incident_model
            "casualties": "none",               # This would come from casualty_model
            "priority": 3.5,                    # This would be calculated based on incident and casualties
            "priority_level": "HIGH"            # This would be mapped from the priority score
        }
    
    def _print_interpretation(self, result):
        """Print a formatted version of the interpretation result."""
        print("\n" + "="*60)
        print("EMERGENCY CALL INTERPRETATION")
        print("="*60)
        
        print(f"INCIDENT TYPE: {result.get('incident_type', 'UNKNOWN').upper()}")
        
        # Print address information (now enhanced with validation)
        address = result.get('reverse_geocoded_address', 'Unknown address')
        landmark = result.get('landmark', '')
        
        if landmark:
            print(f"LOCATION: {address} (Landmark: {landmark})")
        else:
            print(f"LOCATION: {address}")
            
        print(f"JURISDICTION: {result.get('jurisdiction', 'Unknown')}")
        print(f"ZIP CODE: {result.get('matched_zip', 'Unknown')}")
        print(f"ADDRESS CONFIDENCE: {result.get('address_confidence', 0):.2f}")
        
        print(f"CASUALTIES: {result.get('casualties', 'Unknown')}")
        print(f"PRIORITY: {result.get('priority_level', 'UNKNOWN')} ({result.get('priority', 0):.1f})")
        
        verification = "REQUIRES VERIFICATION" if result.get('needs_verification', True) else "VERIFIED"
        print(f"STATUS: {verification}")
        
        print("="*60 + "\n")
    
    def _save_interpretation(self, result):
        """Save the interpretation to a file."""
        # Create a filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/interpretation_{timestamp}.json"
        
        # Write the result to a JSON file
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Also update the session log
        session_filename = f"{self.output_dir}/session_{self.current_session}.json"
        with open(session_filename, 'w') as f:
            json.dump(self.interpretation_log, f, indent=2)
    
    def _add_to_verification_queue(self, result):
        """Add an interpretation to the verification queue."""
        self.verification_queue.append(result)
        
        # Save to verification directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/needs_verification/verify_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Added to verification queue: {result.get('incident_type', 'Unknown incident')}")
    
    def get_verification_queue(self):
        """Get the current verification queue."""
        return self.verification_queue 
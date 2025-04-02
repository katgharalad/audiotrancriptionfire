import os
import json
import datetime
from interpret_function import interpret_transcript

class AudioTranscriptInterpreter:
    """
    Integration layer that processes transcripts from AudioTranscripY
    and interprets them using the trained ML models.
    """
    def __init__(self, output_dir="interpretations", verification_threshold=0.7):
        """
        Initialize the interpreter.
        
        Args:
            output_dir (str): Directory to save interpretations
            verification_threshold (float): Confidence threshold for verification
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
        
        self.current_session = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.interpretation_log = []
        
        print(f"AudioTranscriptInterpreter initialized. Output directory: {output_dir}")
        print("Ready to process transcripts. Waiting for input...")
    
    def process_transcript(self, transcript_text):
        """
        Process a single transcript and return the interpretation.
        Only processes transcripts from Speaker 2 (the caller).
        
        Args:
            transcript_text (str): Raw transcript text
            
        Returns:
            dict: Interpretation result or None if not from Speaker 2
        """
        # Only process if the transcript is from Speaker 2 (the caller)
        if not transcript_text.startswith("Speaker 2:"):
            print("Ignored transcript (not from caller)")
            return None
        
        # Use the trained model to interpret the transcript
        result = interpret_transcript(transcript_text)
        
        if result:
            # Add timestamp
            result['timestamp'] = datetime.datetime.now().isoformat()
            result['transcript'] = transcript_text
            
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
    
    def _print_interpretation(self, result):
        """Print a formatted version of the interpretation result."""
        print("\n" + "="*50)
        print("EMERGENCY CALL INTERPRETATION")
        print("="*50)
        print(f"INCIDENT TYPE: {result['incident_type'].upper()}")
        if 'incident_type_confidence' in result:
            print(f"CONFIDENCE: {result['incident_type_confidence']:.2f}")
        
        print(f"LOCATION: {result['address']}")
        if 'address_validation' in result:
            valid = result['address_validation']['valid']
            conf = result['address_validation']['confidence']
            print(f"ADDRESS VALID: {valid} (Confidence: {conf:.2f})")
        
        print(f"CASUALTIES: {result['casualties']}")
        if 'casualties_structured' in result:
            struct = result['casualties_structured']
            categories = []
            if struct['children']: categories.append("Children")
            if struct['elderly']: categories.append("Elderly")
            if struct['pets']: categories.append("Pets")
            if struct['caller']: categories.append("Caller")
            if categories:
                print(f"AFFECTED: {', '.join(categories)}")
        
        if 'priority' in result and 'priority_level' in result:
            print(f"PRIORITY: {result['priority_level']} ({result['priority']})")
        
        if 'needs_verification' in result:
            verification = "REQUIRES VERIFICATION" if result['needs_verification'] else "VERIFIED"
            print(f"STATUS: {verification}")
        
        print("="*50 + "\n")
    
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
        
        print(f"Added to verification queue: {result['incident_type']}")
    
    def get_verification_queue(self):
        """Get the current verification queue."""
        return self.verification_queue
    
    def process_batch(self, transcript_list):
        """
        Process a batch of transcripts.
        
        Args:
            transcript_list (list): List of transcript strings
        
        Returns:
            list: List of interpretation results
        """
        results = []
        for transcript in transcript_list:
            result = self.process_transcript(transcript)
            if result:
                results.append(result)
        return results
    
    def get_high_priority_incidents(self, min_priority=4.0):
        """
        Get high priority incidents from the current session.
        
        Args:
            min_priority (float): Minimum priority threshold
            
        Returns:
            list: High priority interpretations
        """
        high_priority = []
        
        for interp in self.interpretation_log:
            if 'priority' in interp and interp['priority'] >= min_priority:
                high_priority.append(interp)
        
        return high_priority


# Demo usage
if __name__ == "__main__":
    # Create the interpreter
    interpreter = AudioTranscriptInterpreter()
    
    # Example transcripts for testing
    test_transcripts = [
        "Speaker 1: This is the dispatcher. What's your emergency?",
        "Speaker 2: There's a kitchen fire at 123 Oak Street. My wife is trapped in the bathroom.",
        "Speaker 1: Is there smoke or flames visible?",
        "Speaker 2: Yes, flames are coming from the stove and spreading to the cabinets.",
        "Speaker 3: I can confirm there's a structure fire at this address.",
        "Speaker 2: The fire is getting worse. Please hurry!"
    ]
    
    # Process each transcript
    for transcript in test_transcripts:
        interpreter.process_transcript(transcript)
    
    # Check verification queue
    verification_queue = interpreter.get_verification_queue()
    if verification_queue:
        print(f"\nVerification Queue: {len(verification_queue)} items")
        for item in verification_queue:
            print(f"- {item['incident_type']} at {item['address']}")
    
    # Check high priority incidents
    high_priority = interpreter.get_high_priority_incidents()
    if high_priority:
        print(f"\nHigh Priority Incidents: {len(high_priority)}")
        for item in high_priority:
            print(f"- {item['incident_type']} ({item['priority_level']}) at {item['address']}")
    
    print("\nAll transcripts processed. Check the 'interpretations' directory for results.") 
import os
import sys
import json
import re
from datetime import datetime

class EmergencyProcessor:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "interpretation_outputs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_transcript(self, transcript):
        """Process a transcript and extract emergency information."""
        print(f"Processing transcript: {transcript[:50]}...")
        
        # Example extraction logic
        incident_type = self.extract_incident_type(transcript)
        address = self.extract_address(transcript)
        casualties = self.extract_casualties(transcript)
        
        result = {
            "incident_type": incident_type,
            "address": address,
            "casualties": casualties,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "transcript": transcript[:300] + "..." if len(transcript) > 300 else transcript
        }
        
        # Save result
        self.save_result(result)
        return result
    
    def extract_incident_type(self, text):
        """Extract incident type from text."""
        text = text.lower()
        if "kitchen fire" in text or ("fire" in text and "kitchen" in text):
            return "kitchen fire"
        elif "structure fire" in text or ("fire" in text and ("building" in text or "house" in text)):
            return "structure fire"
        elif "gas leak" in text:
            return "gas leak"
        elif "fire" in text:
            return "structure fire"
        return "unknown"
    
    def extract_address(self, text):
        """Extract address from text."""
        # Simple pattern for addresses
        address_pattern = r'(\d+\s+[a-zA-Z\s]+(street|st|avenue|ave|road|rd|lane|ln|drive|dr))'
        match = re.search(address_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return "unknown address"
    
    def extract_casualties(self, text):
        """Extract casualties information from text."""
        text = text.lower()
        if "no casualties" in text or "no one" in text:
            return "none"
        elif "children" in text and "trapped" in text:
            return "children trapped"
        elif "trapped" in text:
            return "people trapped"
        elif "injured" in text:
            return "people injured"
        return "unknown"
    
    def save_result(self, result):
        """Save processing result to a file."""
        if not self.output_dir:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"emergency_{timestamp}.json")
        
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"Result saved to {filename}")

if __name__ == "__main__":
    # Example usage
    processor = EmergencyProcessor()
    result = processor.process_transcript("There's a kitchen fire at 123 Main St. Two people are trapped inside.")
    print(json.dumps(result, indent=2))
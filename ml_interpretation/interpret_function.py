import pickle
import re
import os

# Import enhanced features
from enhanced_features import (
    add_confidence_scores,
    needs_verification,
    AddressValidator,
    PriorityPredictor,
    CasualtyStructurer
)

# Load the trained models
with open('incident_model.pkl', 'rb') as f:
    incident_pipeline = pickle.load(f)

with open('casualties_model.pkl', 'rb') as f:
    casualties_pipeline = pickle.load(f)

# Initialize enhanced features
address_validator = AddressValidator()
priority_predictor = PriorityPredictor(model_type="rule")
casualty_structurer = CasualtyStructurer()

def preprocess_transcript(text):
    """Clean transcript by removing speaker prefix and standardizing text"""
    if not isinstance(text, str):
        return ""
    # Extract text after speaker prefix (e.g., "Speaker 2: ")
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation that doesn't affect meaning
    text = re.sub(r'[^\w\s]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def interpret_transcript(text):
    """
    Process a transcript to identify incident type, address, and casualties.
    Returns a dictionary with the extracted information and enhanced features.
    
    Args:
        text (str): Raw transcript text, e.g., "Speaker 2: There's a fire at 123 Main St."
        
    Returns:
        dict: Enhanced interpretation with confidence scores, structured casualties, etc.
    """
    # Only process if the transcript is from Speaker 2 (the caller)
    if not text.startswith("Speaker 2:"):
        return None
        
    # Clean the input text
    clean_text = preprocess_transcript(text)
    
    # Predict incident type with confidence
    incident_type = incident_pipeline.predict([clean_text])[0]
    incident_proba = None
    
    # Get probabilities if available (for confidence scores)
    try:
        incident_proba = incident_pipeline.predict_proba([clean_text])[0]
    except:
        print("Warning: Could not get incident type probabilities")
    
    # Predict casualties with confidence
    casualties = casualties_pipeline.predict([clean_text])[0]
    casualties_proba = None
    
    try:
        casualties_proba = casualties_pipeline.predict_proba([clean_text])[0]
    except:
        print("Warning: Could not get casualties probabilities")
    
    # Extract address using regex pattern
    address_pattern = r'(?:at|in|on|near)\s+([0-9]+\s+[\w\s\.]+(?:avenue|ave|street|st|road|rd|drive|dr|lane|ln|way|place|pl|circle|cir|court|ct|boulevard|blvd|highway|hwy)\.?)'
    address_match = re.search(address_pattern, text.lower())
    raw_address = address_match.group(1).strip() if address_match else "Unknown address"
    
    # Create basic interpretation (legacy format)
    basic_interp = {
        "incident_type": incident_type,
        "address": raw_address,
        "casualties": casualties
    }
    
    # Step 1: Add confidence scores
    probabilities = {}
    if incident_proba is not None:
        probabilities["incident_type_proba"] = incident_proba.tolist()
    if casualties_proba is not None:
        probabilities["casualties_proba"] = casualties_proba.tolist()
    
    enhanced_interp = add_confidence_scores(basic_interp, probabilities)
    
    # Step 2: Validate and normalize address
    address_validation = address_validator.validate_address(raw_address)
    enhanced_interp["address"] = address_validation["normalized_address"]
    enhanced_interp["address_validation"] = {
        "valid": address_validation["valid"],
        "confidence": address_validation["confidence"],
        "needs_verification": address_validation["needs_verification"]
    }
    
    # Step 3: Determine priority based on incident type and casualties
    priority_info = priority_predictor.predict_priority(incident_type, casualties)
    enhanced_interp["priority"] = priority_info["priority"]
    enhanced_interp["priority_level"] = priority_info["priority_level"]
    
    # Step 4: Structure casualties info
    structured_casualties = casualty_structurer.structure_casualties(casualties)
    enhanced_interp["casualties_structured"] = {
        "children": structured_casualties["children"],
        "elderly": structured_casualties["elderly"],
        "pets": structured_casualties["pets"],
        "caller": structured_casualties["caller"]
    }
    
    # Step 5: Overall verification flag
    enhanced_interp["needs_verification"] = (
        needs_verification(enhanced_interp) or 
        address_validation["needs_verification"]
    )
    
    return enhanced_interp

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import pickle
import re

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('delaware_fire_incidents_full.csv')

# Data preprocessing
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

print("Preprocessing transcripts...")
df['clean_transcript'] = df['transcript'].apply(preprocess_transcript)

# Filter to only include Speaker 2 transcripts (the caller)
print("Filtering for Speaker 2 (caller) transcripts...")
caller_df = df[df['reporter'] == 'Speaker 2'].reset_index(drop=True)
print(f"Number of caller transcripts: {len(caller_df)}")

# Prepare features and targets
X = caller_df['clean_transcript']
y_incident = caller_df['incident_type']
y_casualties = caller_df['casualties'] 

# Split the data
print("Splitting data into train and test sets...")
X_train, X_test, y_train_incident, y_test_incident, y_train_casualties, y_test_casualties = train_test_split(
    X, y_incident, y_casualties, test_size=0.2, random_state=42
)

# Create a pipeline for incident type prediction
print("Building incident type classifier...")
incident_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Train incident type model
print("Training incident type model...")
incident_pipeline.fit(X_train, y_train_incident)

# Create a pipeline for casualties prediction
print("Building casualties classifier...")
casualties_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Train casualties model
print("Training casualties model...")
casualties_pipeline.fit(X_train, y_train_casualties)

# Evaluate the models
print("\nEvaluating models...")
# Incident type evaluation
y_pred_incident = incident_pipeline.predict(X_test)
incident_accuracy = accuracy_score(y_test_incident, y_pred_incident)
print(f"Incident Type Accuracy: {incident_accuracy:.4f}")
print("Incident Type Classification Report:")
print(classification_report(y_test_incident, y_pred_incident))

# Casualties evaluation
y_pred_casualties = casualties_pipeline.predict(X_test)
casualties_accuracy = accuracy_score(y_test_casualties, y_pred_casualties)
print(f"Casualties Accuracy: {casualties_accuracy:.4f}")
print("Casualties Classification Report:")
print(classification_report(y_test_casualties, y_pred_casualties))

# Save the models
print("Saving models...")
with open('incident_model.pkl', 'wb') as f:
    pickle.dump(incident_pipeline, f)

with open('casualties_model.pkl', 'wb') as f:
    pickle.dump(casualties_pipeline, f)

# Create a function to interpret transcripts
def interpret_transcript(text):
    """
    Process a transcript to identify incident type, address, and casualties.
    Returns a dictionary with the extracted information.
    """
    # Clean the input text
    clean_text = preprocess_transcript(text)
    
    # Predict incident type
    incident_type = incident_pipeline.predict([clean_text])[0]
    
    # Predict casualties
    casualties = casualties_pipeline.predict([clean_text])[0]
    
    # Extract address using regex pattern
    address_pattern = r'(?:at|in|on|near)\s+([0-9]+\s+[\w\s\.]+(?:avenue|ave|street|st|road|rd|drive|dr|lane|ln|way|place|pl|circle|cir|court|ct|boulevard|blvd|highway|hwy)\.?)'
    address_match = re.search(address_pattern, text.lower())
    address = address_match.group(1).strip() if address_match else "Unknown address"
    
    return {
        "incident_type": incident_type,
        "address": address,
        "casualties": casualties
    }

# Save the interpretation function in a separate file
with open('interpret_function.py', 'w') as f:
    f.write("""import pickle
import re

# Load the trained models
with open('incident_model.pkl', 'rb') as f:
    incident_pipeline = pickle.load(f)

with open('casualties_model.pkl', 'rb') as f:
    casualties_pipeline = pickle.load(f)

def preprocess_transcript(text):
    \"\"\"Clean transcript by removing speaker prefix and standardizing text\"\"\"
    if not isinstance(text, str):
        return ""
    # Extract text after speaker prefix (e.g., "Speaker 2: ")
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation that doesn't affect meaning
    text = re.sub(r'[^\\w\\s]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

def interpret_transcript(text):
    \"\"\"
    Process a transcript to identify incident type, address, and casualties.
    Returns a dictionary with the extracted information.
    
    Args:
        text (str): Raw transcript text, e.g., "Speaker 2: There's a fire at 123 Main St."
        
    Returns:
        dict: Dictionary with keys 'incident_type', 'address', and 'casualties'
    \"\"\"
    # Only process if the transcript is from Speaker 2 (the caller)
    if not text.startswith("Speaker 2:"):
        return None
        
    # Clean the input text
    clean_text = preprocess_transcript(text)
    
    # Predict incident type
    incident_type = incident_pipeline.predict([clean_text])[0]
    
    # Predict casualties
    casualties = casualties_pipeline.predict([clean_text])[0]
    
    # Extract address using regex pattern
    address_pattern = r'(?:at|in|on|near)\\s+([0-9]+\\s+[\\w\\s\\.]+(?:avenue|ave|street|st|road|rd|drive|dr|lane|ln|way|place|pl|circle|cir|court|ct|boulevard|blvd|highway|hwy)\\.?)'
    address_match = re.search(address_pattern, text.lower())
    address = address_match.group(1).strip() if address_match else "Unknown address"
    
    return {
        "incident_type": incident_type,
        "address": address,
        "casualties": casualties
    }
""")

print("\nComplete! Created the following files:")
print("1. incident_model.pkl - Trained model for incident type classification")
print("2. casualties_model.pkl - Trained model for casualties classification")
print("3. interpret_function.py - Module with the interpret_transcript() function") 
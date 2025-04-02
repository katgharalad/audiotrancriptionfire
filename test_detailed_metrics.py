import pandas as pd
import numpy as np
import pickle
import re
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, 
    classification_report, 
    f1_score, 
    accuracy_score, 
    precision_score, 
    recall_score,
    roc_curve, 
    auc,
    precision_recall_curve
)
from sklearn.model_selection import train_test_split
from interpret_function import interpret_transcript, preprocess_transcript
from main import AudioTranscriptInterpreter
import time

def perform_metrics_test():
    # Create outputs directory
    output_dir = "test_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the trained models
    with open('incident_model.pkl', 'rb') as f:
        incident_model = pickle.load(f)

    with open('casualties_model.pkl', 'rb') as f:
        casualties_model = pickle.load(f)

    # Load the dataset
    print("Loading dataset...")
    df = pd.read_csv('delaware_fire_incidents_full.csv')

    # Filter for Speaker 2 transcripts
    caller_df = df[df['reporter'] == 'Speaker 2'].reset_index(drop=True)
    print(f"Total samples: {len(df)}")
    print(f"Speaker 2 (caller) samples: {len(caller_df)}")

    # Prepare data
    caller_df['clean_transcript'] = caller_df['transcript'].apply(preprocess_transcript)
    X = caller_df['clean_transcript']
    y_incident = caller_df['incident_type']
    y_casualties = caller_df['casualties']

    # Use the same random state to match the test set from model_training.py
    _, X_test, _, y_incident_test, _, y_casualties_test = train_test_split(
        X, y_incident, y_casualties, test_size=0.2, random_state=42
    )

    print(f"Test set size: {len(X_test)}")

    # Performance Metrics
    print("\n================ PERFORMANCE METRICS ================")
    # Measure prediction speed (latency)
    start_time = time.time()
    incident_pred = incident_model.predict(X_test)
    casualties_pred = casualties_model.predict(X_test)
    end_time = time.time()

    prediction_time = end_time - start_time
    avg_prediction_time = prediction_time / len(X_test)
    print(f"Total prediction time for {len(X_test)} samples: {prediction_time:.4f} seconds")
    print(f"Average prediction time per sample: {avg_prediction_time*1000:.4f} ms")

    # Calculate metrics
    incident_accuracy = accuracy_score(y_incident_test, incident_pred)
    incident_precision = precision_score(y_incident_test, incident_pred, average='weighted')
    incident_recall = recall_score(y_incident_test, incident_pred, average='weighted')
    incident_f1 = f1_score(y_incident_test, incident_pred, average='weighted')

    casualties_accuracy = accuracy_score(y_casualties_test, casualties_pred)
    casualties_precision = precision_score(y_casualties_test, casualties_pred, average='weighted')
    casualties_recall = recall_score(y_casualties_test, casualties_pred, average='weighted')
    casualties_f1 = f1_score(y_casualties_test, casualties_pred, average='weighted')

    print("\n---- Incident Type Classification ----")
    print(f"Accuracy: {incident_accuracy:.4f}")
    print(f"Precision: {incident_precision:.4f}")
    print(f"Recall: {incident_recall:.4f}")
    print(f"F1 Score: {incident_f1:.4f}")

    print("\n---- Casualties Classification ----")
    print(f"Accuracy: {casualties_accuracy:.4f}")
    print(f"Precision: {casualties_precision:.4f}")
    print(f"Recall: {casualties_recall:.4f}")
    print(f"F1 Score: {casualties_f1:.4f}")

    # Address Extraction Testing
    print("\n================ ADDRESS EXTRACTION TESTING ================")
    # Create samples with known addresses
    address_test_samples = [
        "Speaker 2: There's a kitchen fire at 123 Main Street. No one is hurt.",
        "Speaker 2: Gas leak reported at 456 Oak Avenue apt 7B. Everyone has evacuated.",
        "Speaker 2: Structural fire at 789 Washington Boulevard. Elderly person trapped inside.",
        "Speaker 2: Vehicle fire at 10 Liberty Lane. The caller is trapped.",
        "Speaker 2: Wildfire reported near 55 Pinecrest Drive. Children are in danger."
    ]

    print("Testing address extraction...")
    address_results = []
    for sample in address_test_samples:
        result = interpret_transcript(sample)
        if result:
            address_results.append({
                "transcript": sample,
                "extracted_address": result["address"],
                "incident_type": result["incident_type"],
                "casualties": result["casualties"]
            })
            print(f"Sample: {sample}")
            print(f"Extracted address: {result['address']}")
            print(f"Incident type: {result['incident_type']}")
            print(f"Casualties: {result['casualties']}")
            print("-" * 50)

    # Save address test results
    with open(f"{output_dir}/address_extraction_results.json", "w") as f:
        json.dump(address_results, f, indent=2)

    # Create confusion matrices
    print("\n================ CONFUSION MATRICES ================")
    incident_cm = confusion_matrix(y_incident_test, incident_pred)
    casualties_cm = confusion_matrix(y_casualties_test, casualties_pred)

    # Plot incident type confusion matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(incident_cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=sorted(caller_df['incident_type'].unique()),
                yticklabels=sorted(caller_df['incident_type'].unique()))
    plt.title('Incident Type Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/incident_confusion_matrix.png")

    # Plot casualties confusion matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(casualties_cm, annot=True, fmt='d', cmap='Greens',
                xticklabels=sorted(caller_df['casualties'].unique()),
                yticklabels=sorted(caller_df['casualties'].unique()))
    plt.title('Casualties Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/casualties_confusion_matrix.png")

    print(f"Confusion matrices saved to {output_dir}/")

    # Test full pipeline with various test cases
    print("\n================ FULL PIPELINE TESTING ================")
    # Initialize interpreter
    interpreter = AudioTranscriptInterpreter(output_dir=f"{output_dir}/interpretations")

    # Test cases covering different scenarios
    test_cases = [
        # Basic cases
        "Speaker 2: There's a kitchen fire at 123 Main Street. No one is hurt.",
        "Speaker 2: Structure fire at 456 Elm Road. My wife is trapped upstairs.",
        "Speaker 2: Gas leak at 789 Oak Avenue. The whole family evacuated.",
        
        # Edge cases
        "Speaker 2: I'm not sure what's happening but there's smoke everywhere at 101 Pine Street.",
        "Speaker 2: The building at 202 Maple Drive is on fire and there might be people inside.",
        
        # Multiple pieces of information
        "Speaker 2: There's a fire at 303 Cherry Lane. It started in the kitchen but spread to the living room. My dog is still inside.",
        
        # Non-caller speakers (should be ignored)
        "Speaker 1: What's your emergency?",
        "Speaker 3: I can confirm there's a fire at this location.",
        
        # Address variations
        "Speaker 2: Fire at 505 Washington Blvd apt 3C. Children trapped.",
        "Speaker 2: Car on fire at 606 Jefferson St. No injuries."
    ]

    print("Processing test cases through the interpreter...")
    for test_case in test_cases:
        print(f"\nInput: {test_case}")
        result = interpreter.process_transcript(test_case)
        if not result:
            print("No result (non-Speaker 2 or processing failed)")

    print(f"\nFull pipeline test results saved to {output_dir}/interpretations/")

    # Summarize metrics in a JSON file
    metrics = {
        "test_set_size": len(X_test),
        "latency": {
            "total_prediction_time_seconds": prediction_time,
            "average_prediction_time_ms": avg_prediction_time * 1000
        },
        "incident_type_classification": {
            "accuracy": incident_accuracy,
            "precision": incident_precision,
            "recall": incident_recall,
            "f1_score": incident_f1
        },
        "casualties_classification": {
            "accuracy": casualties_accuracy,
            "precision": casualties_precision,
            "recall": casualties_recall,
            "f1_score": casualties_f1
        }
    }

    with open(f"{output_dir}/metrics_summary.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Metrics summary saved to {output_dir}/metrics_summary.json")
    print("\nDetailed testing complete!")
    
    return metrics

if __name__ == "__main__":
    perform_metrics_test() 
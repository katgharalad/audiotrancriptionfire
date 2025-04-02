import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, f1_score, accuracy_score
import pickle
import os
import re
from datetime import datetime

# Load the trained models
with open('incident_model.pkl', 'rb') as f:
    incident_model = pickle.load(f)

with open('casualties_model.pkl', 'rb') as f:
    casualties_model = pickle.load(f)

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('delaware_fire_incidents_full.csv')

# Preprocess function
def preprocess_transcript(text):
    """Clean transcript by removing speaker prefix and standardizing text"""
    if not isinstance(text, str):
        return ""
    # Extract text after speaker prefix
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation that doesn't affect meaning
    text = re.sub(r'[^\w\s]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Filter for Speaker 2 transcripts
caller_df = df[df['reporter'] == 'Speaker 2'].reset_index(drop=True)
print(f"Total samples: {len(df)}")
print(f"Speaker 2 (caller) samples: {len(caller_df)}")

# Prepare test data (20% of the dataset)
caller_df['clean_transcript'] = caller_df['transcript'].apply(preprocess_transcript)
X = caller_df['clean_transcript']
y_incident = caller_df['incident_type']
y_casualties = caller_df['casualties']

# Use a fixed random state to match the test set from model_training.py
from sklearn.model_selection import train_test_split
_, X_test, _, y_incident_test, _, y_casualties_test = train_test_split(
    X, y_incident, y_casualties, test_size=0.2, random_state=42
)

# Make predictions
print("\nMaking predictions on test set...")
incident_pred = incident_model.predict(X_test)
casualties_pred = casualties_model.predict(X_test)

# Calculate metrics
incident_accuracy = accuracy_score(y_incident_test, incident_pred)
incident_f1 = f1_score(y_incident_test, incident_pred, average='weighted')
casualties_accuracy = accuracy_score(y_casualties_test, casualties_pred)
casualties_f1 = f1_score(y_casualties_test, casualties_pred, average='weighted')

print(f"Incident Type Accuracy: {incident_accuracy:.4f}")
print(f"Incident Type F1 Score: {incident_f1:.4f}")
print(f"Casualties Accuracy: {casualties_accuracy:.4f}")
print(f"Casualties F1 Score: {casualties_f1:.4f}")

# Create confusion matrices
incident_cm = confusion_matrix(y_incident_test, incident_pred)
casualties_cm = confusion_matrix(y_casualties_test, casualties_pred)

# Sample predictions with actual values
print("\nSample predictions (5 random examples):")
sample_indices = np.random.choice(len(X_test), 5, replace=False)
for idx in sample_indices:
    text = X_test.iloc[idx]
    true_incident = y_incident_test.iloc[idx]
    pred_incident = incident_pred[idx]
    true_casualties = y_casualties_test.iloc[idx]
    pred_casualties = casualties_pred[idx]
    
    print(f"\nTranscript: {text}")
    print(f"True Incident: {true_incident}, Predicted: {pred_incident}")
    print(f"True Casualties: {true_casualties}, Predicted: {pred_casualties}")

# Generate a detailed report
print("\nGenerating evaluation report...")
report_dir = "reports"
if not os.path.exists(report_dir):
    os.makedirs(report_dir)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_file = f"{report_dir}/model_evaluation_{timestamp}.md"

with open(report_file, 'w') as f:
    f.write("# Fire Incident ML Model Evaluation\n\n")
    f.write(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
    
    f.write("## Dataset Statistics\n\n")
    f.write(f"- Total samples: {len(df)}\n")
    f.write(f"- Speaker 2 (caller) samples: {len(caller_df)}\n")
    f.write(f"- Test set size: {len(X_test)}\n\n")
    
    f.write("## Incident Type Classification\n\n")
    f.write(f"- Accuracy: {incident_accuracy:.4f}\n")
    f.write(f"- F1 Score (weighted): {incident_f1:.4f}\n\n")
    
    f.write("**Classification Report:**\n\n")
    f.write("```\n")
    f.write(classification_report(y_incident_test, incident_pred))
    f.write("```\n\n")
    
    f.write("## Casualties Classification\n\n")
    f.write(f"- Accuracy: {casualties_accuracy:.4f}\n")
    f.write(f"- F1 Score (weighted): {casualties_f1:.4f}\n\n")
    
    f.write("**Classification Report:**\n\n")
    f.write("```\n")
    f.write(classification_report(y_casualties_test, casualties_pred))
    f.write("```\n\n")
    
    f.write("## Sample Predictions\n\n")
    for idx in sample_indices:
        text = X_test.iloc[idx]
        true_incident = y_incident_test.iloc[idx]
        pred_incident = incident_pred[idx]
        true_casualties = y_casualties_test.iloc[idx]
        pred_casualties = casualties_pred[idx]
        
        f.write(f"### Example {idx}\n\n")
        f.write(f"**Transcript:** {text}\n\n")
        f.write(f"**Incident Type:**\n- True: {true_incident}\n- Predicted: {pred_incident}\n\n")
        f.write(f"**Casualties:**\n- True: {true_casualties}\n- Predicted: {pred_casualties}\n\n")
    
    f.write("## Conclusion\n\n")
    if incident_accuracy > 0.95 and casualties_accuracy > 0.95:
        f.write("The models show excellent performance on the test data. They are ready for deployment in a fire dispatch environment.\n\n")
    elif incident_accuracy > 0.85 and casualties_accuracy > 0.85:
        f.write("The models show good performance but could benefit from additional training or fine-tuning before production deployment.\n\n")
    else:
        f.write("The models show suboptimal performance. Further data collection and model improvements are recommended before deployment.\n\n")
        
print(f"Evaluation report saved to {report_file}")

# Create plots directory
plots_dir = "plots"
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

# Plot incident type distribution
plt.figure(figsize=(10, 6))
incident_counts = df['incident_type'].value_counts()
incident_counts.plot(kind='bar', color='skyblue')
plt.title('Incident Type Distribution')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f"{plots_dir}/incident_type_distribution.png")

# Plot casualties distribution
plt.figure(figsize=(10, 6))
casualties_counts = df['casualties'].value_counts()
casualties_counts.plot(kind='bar', color='lightgreen')
plt.title('Casualties Distribution')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f"{plots_dir}/casualties_distribution.png")

print(f"Plots saved to {plots_dir}/")
print("Evaluation complete!") 
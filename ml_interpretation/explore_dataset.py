import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('delaware_fire_incidents_full.csv')

# Display basic information
print("\nDataset shape:", df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())

# Sample data
print("\nSample data (first 5 rows):")
print(df.head())

# Statistics about incident types
print("\nIncident Type Statistics:")
incident_counts = Counter(df['incident_type'])
for incident, count in incident_counts.most_common():
    print(f"  - {incident}: {count} ({count/len(df)*100:.2f}%)")

# Statistics about casualties
print("\nCasualties Statistics:")
casualties_counts = Counter(df['casualties'])
for casualty, count in casualties_counts.most_common():
    print(f"  - {casualty}: {count} ({count/len(df)*100:.2f}%)")

# Statistics about speakers
print("\nSpeaker Statistics:")
speakers = []
for transcript in df['transcript']:
    if isinstance(transcript, str):
        speaker = transcript.split(':')[0].strip() if ':' in transcript else 'Unknown'
        speakers.append(speaker)
speaker_counts = Counter(speakers)
for speaker, count in speaker_counts.most_common():
    print(f"  - {speaker}: {count} ({count/len(df)*100:.2f}%)")

# Save summary to file
with open('dataset_summary.txt', 'w') as f:
    f.write(f"Dataset shape: {df.shape}\n")
    f.write(f"Column names: {df.columns.tolist()}\n")
    f.write(f"Missing values:\n{df.isnull().sum()}\n\n")
    
    f.write("Incident Type Statistics:\n")
    for incident, count in incident_counts.most_common():
        f.write(f"  - {incident}: {count} ({count/len(df)*100:.2f}%)\n")
    
    f.write("\nCasualties Statistics:\n")
    for casualty, count in casualties_counts.most_common():
        f.write(f"  - {casualty}: {count} ({count/len(df)*100:.2f}%)\n")
        
    f.write("\nSpeaker Statistics:\n")
    for speaker, count in speaker_counts.most_common():
        f.write(f"  - {speaker}: {count} ({count/len(df)*100:.2f}%)\n")

print("\nSummary saved to dataset_summary.txt") 
import os
import sys
import json
from main import AudioTranscriptInterpreter

def process_transcript_file(file_path):
    """
    Process a transcript file with the ML interpretation layer.
    
    Args:
        file_path (str): Path to the transcript file
    """
    # Create the interpreter
    interpreter = AudioTranscriptInterpreter(output_dir="interpretations")
    
    try:
        # Read the transcript file
        with open(file_path, 'r') as f:
            transcripts = f.readlines()
        
        print(f"\nProcessing transcript file: {file_path}")
        print(f"Found {len(transcripts)} lines to process")
        
        # Process each line in the transcript
        for i, transcript in enumerate(transcripts):
            transcript = transcript.strip()
            if not transcript:
                continue
                
            print(f"\nProcessing line {i+1}: {transcript}")
            
            # Add Speaker 2 prefix if not present
            if not transcript.startswith("Speaker"):
                transcript = f"Speaker 2: {transcript}"
            
            # Process with the ML interpreter
            print("\n" + "="*60)
            print("🧠 ML INTERPRETATION".center(60))
            print("="*60)
            
            result = interpreter.process_transcript(transcript)
            
            if not result:
                print("No interpretation available (not from caller or processing failed)")
            
            print("="*60)
            
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
        
        print("\n✅ Transcript processing completed.")
        print("Check the 'interpretations' directory for saved results.")
        
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"Error processing transcript file: {e}")

if __name__ == "__main__":
    print("\n🔥 Transcript to ML Interpretation Tool 🔥")
    print("This tool processes transcript files with the ML interpretation layer.")
    
    if len(sys.argv) > 1:
        # File path provided as command line argument
        transcript_file = sys.argv[1]
        process_transcript_file(transcript_file)
    else:
        # Ask for file path
        transcript_file = input("\nEnter the path to your transcript file: ")
        if os.path.exists(transcript_file):
            process_transcript_file(transcript_file)
        else:
            print(f"Error: File not found: {transcript_file}")
            
            # Option to try the interactive mode instead
            choice = input("\nWould you like to enter a transcript manually instead? (y/n): ")
            if choice.lower() == 'y':
                interpreter = AudioTranscriptInterpreter(output_dir="interpretations")
                
                print("\n🔥 Interactive ML Interpretation 🔥")
                print("Type emergency call transcripts to test the ML interpretation.")
                print("Type 'exit' to quit.\n")
                
                while True:
                    user_input = input("\nEnter transcript (or 'exit' to quit): ")
                    
                    if user_input.lower() == 'exit':
                        break
                    
                    # Add Speaker 2 prefix if not present
                    if not user_input.startswith("Speaker"):
                        user_input = f"Speaker 2: {user_input}"
                    
                    # Process with the ML interpreter
                    print("\n" + "="*60)
                    print("🧠 ML INTERPRETATION".center(60))
                    print("="*60)
                    
                    result = interpreter.process_transcript(user_input)
                    
                    if not result:
                        print("No interpretation available (not from caller or processing failed)")
                    
                    print("="*60)
                
                print("\n✅ Interactive testing completed.")
                print("Check the 'interpretations' directory for saved results.") 
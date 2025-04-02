import os
import sys
import json
import datetime
from interpret_function import interpret_transcript
from main import AudioTranscriptInterpreter

def simulate_transcription():
    """
    Instead of real-time audio capture, simulate a conversation with predefined transcripts.
    This allows testing the ML interpretation layer without the audio dependencies.
    """
    # Create the interpreter
    interpreter = AudioTranscriptInterpreter(output_dir="interpretations")
    
    # Example transcripts for testing
    test_transcripts = [
        "Speaker 1: This is the dispatcher. What's your emergency?",
        "Speaker 2: There's a kitchen fire at 123 Oak Street. My wife is trapped in the bathroom.",
        "Speaker 1: Is there smoke or flames visible?",
        "Speaker 2: Yes, flames are coming from the stove and spreading to the cabinets.",
        "Speaker 3: I can confirm there's a structure fire at this address.",
        "Speaker 2: The fire is getting worse. Please hurry!"
    ]
    
    print("\n🔥 Fire Dispatch ML Interpretation System 🔥")
    print("This demonstration processes pre-defined transcripts to simulate")
    print("how the system would work with real-time audio transcription.")
    print("\nProcessing simulated emergency call transcripts...\n")
    
    # Process each transcript
    for transcript in test_transcripts:
        print(f"\nIncoming transcript: {transcript}")
        
        # Process with the ML interpreter if from Speaker 2
        if transcript.startswith("Speaker 2:"):
            print("\n" + "="*60)
            print("🧠 ML INTERPRETATION".center(60))
            print("="*60)
            
            result = interpreter.process_transcript(transcript)
            
            print("="*60)
        else:
            print("(Skipped - not from caller)")
    
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
    
    print("\n✅ All transcripts processed.")
    print("Check the 'interpretations' directory for saved results.")

def test_live_interpretation():
    """
    Test the ML interpretation directly with user input.
    This allows interactive testing without audio capture.
    """
    interpreter = AudioTranscriptInterpreter(output_dir="interpretations")
    
    print("\n🔥 Interactive Fire Dispatch ML Interpretation System 🔥")
    print("Type emergency call transcripts to test the ML interpretation.")
    print("Each line should start with 'Speaker 2:' to be processed.")
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

if __name__ == "__main__":
    print("\n🔥 Fire Dispatch ML System 🔥")
    print("Choose a testing mode:")
    print("1. Simulate transcription (pre-defined examples)")
    print("2. Test with your own input")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == "1":
        simulate_transcription()
    elif choice == "2":
        test_live_interpretation()
    else:
        print("Invalid choice. Defaulting to simulation mode.")
        simulate_transcription() 
import pandas as pd
import numpy as np
import time
import json
import os
import random
from interpret_function import interpret_transcript
from main import AudioTranscriptInterpreter

class AudioSimulator:
    """
    Simulates real-time audio transcription from the Whisper model
    to test the ML interpretation layer without requiring actual audio input.
    """
    def __init__(self, dataset_path='delaware_fire_incidents_full.csv', output_dir='audio_simulation'):
        """Initialize the audio simulator."""
        self.df = pd.read_csv(dataset_path)
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Initialize the interpreter
        self.interpreter = AudioTranscriptInterpreter(output_dir=f"{output_dir}/interpretations")
        
        # Filter to only include Speaker 2 transcripts (the caller)
        self.caller_transcripts = self.df[self.df['reporter'] == 'Speaker 2']['transcript'].tolist()
        
        print(f"Audio Simulator initialized with {len(self.caller_transcripts)} caller transcripts")
        print(f"Output directory: {output_dir}")
        
    def simulate_conversation(self, duration_seconds=60, avg_transcript_interval=5):
        """
        Simulate a conversation with transcripts arriving at realistic intervals.
        
        Args:
            duration_seconds (int): Total duration to simulate in seconds
            avg_transcript_interval (int): Average seconds between transcript chunks
        """
        print(f"\nStarting audio simulation for {duration_seconds} seconds...")
        print(f"Average transcript interval: {avg_transcript_interval} seconds")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # Track metrics
        metrics = {
            "total_transcripts": 0,
            "caller_transcripts": 0,
            "non_caller_transcripts": 0,
            "interpretations_generated": 0,
            "avg_interpretation_time": 0,
            "interpretation_times": []
        }
        
        conversation = []
        
        while time.time() < end_time:
            # Randomly select a transcript
            if random.random() < 0.8:  # 80% chance it's from the caller (Speaker 2)
                transcript = random.choice(self.caller_transcripts)
                metrics["caller_transcripts"] += 1
            else:  # 20% chance it's from someone else
                speaker = random.choice(["Speaker 1", "Speaker 3", "Speaker 4"])
                if speaker == "Speaker 1":
                    transcript = f"{speaker}: What's your emergency?" if random.random() < 0.5 else f"{speaker}: Can you provide more details?"
                else:
                    transcript = f"{speaker}: I can confirm there's an incident at this location."
                metrics["non_caller_transcripts"] += 1
            
            metrics["total_transcripts"] += 1
            
            # Print the incoming transcript
            print(f"\n[{time.time() - start_time:.2f}s] TRANSCRIPT: {transcript}")
            
            # Process with the interpreter and time it
            interpretation_start = time.time()
            result = self.interpreter.process_transcript(transcript)
            interpretation_time = time.time() - interpretation_start
            
            if result:
                metrics["interpretations_generated"] += 1
                metrics["interpretation_times"].append(interpretation_time)
                
                # Add to conversation log
                conversation.append({
                    "timestamp": time.time() - start_time,
                    "transcript": transcript,
                    "interpretation": result
                })
            
            # Wait for a random interval
            interval = max(0.5, random.normalvariate(avg_transcript_interval, 1.5))
            remaining_time = end_time - time.time()
            if remaining_time <= 0:
                break
                
            time.sleep(min(interval, remaining_time))
        
        # Calculate average interpretation time
        if metrics["interpretation_times"]:
            metrics["avg_interpretation_time"] = sum(metrics["interpretation_times"]) / len(metrics["interpretation_times"])
        
        # Save simulation results
        simulation_results = {
            "metrics": metrics,
            "conversation": conversation,
            "duration": time.time() - start_time
        }
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"{self.output_dir}/simulation_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(simulation_results, f, indent=2)
        
        print("\nSimulation complete!")
        print(f"Total transcripts: {metrics['total_transcripts']}")
        print(f"Caller transcripts: {metrics['caller_transcripts']}")
        print(f"Non-caller transcripts: {metrics['non_caller_transcripts']}")
        print(f"Interpretations generated: {metrics['interpretations_generated']}")
        print(f"Average interpretation time: {metrics['avg_interpretation_time']*1000:.2f} ms")
        print(f"Results saved to {results_file}")
        
        return simulation_results
    
    def simulate_emergency_scenario(self, scenario_type=None):
        """
        Simulate a specific emergency scenario with a predefined sequence of transcripts.
        
        Args:
            scenario_type (str): Type of scenario to simulate (kitchen_fire, gas_leak, etc.)
                                If None, a random scenario is selected.
        """
        # Define scenario templates
        scenarios = {
            "kitchen_fire": [
                ("Speaker 1", "911, what's your emergency?"),
                ("Speaker 2", "There's a fire in my kitchen at 123 Maple Drive. The stove caught fire."),
                ("Speaker 1", "Is everyone out of the house?"),
                ("Speaker 2", "My wife is still inside, she's trapped in the upstairs bedroom."),
                ("Speaker 1", "Are there flames or just smoke?"),
                ("Speaker 2", "There are flames coming from the stove and spreading to the cabinets."),
                ("Speaker 3", "I can confirm visual on smoke from the property."),
                ("Speaker 2", "The fire is getting worse! Please hurry!")
            ],
            "gas_leak": [
                ("Speaker 1", "911, what's your emergency?"),
                ("Speaker 2", "I smell gas in my house at 456 Oak Avenue."),
                ("Speaker 1", "Have you evacuated the building?"),
                ("Speaker 2", "Yes, we're all outside now."),
                ("Speaker 1", "Did you turn off any appliances?"),
                ("Speaker 2", "No, I just got everyone out as quickly as possible."),
                ("Speaker 4", "I can confirm strong gas odor at this location."),
                ("Speaker 2", "The smell is getting stronger even from outside.")
            ],
            "vehicle_fire": [
                ("Speaker 1", "911, what's your emergency?"),
                ("Speaker 2", "My car is on fire in the parking lot at 789 Main Street."),
                ("Speaker 1", "Is anyone inside the vehicle?"),
                ("Speaker 2", "No, but it's close to other cars and could spread."),
                ("Speaker 1", "How large is the fire?"),
                ("Speaker 2", "The hood is completely engulfed and I can see flames."),
                ("Speaker 3", "Fire is visible from the east side of the parking lot."),
                ("Speaker 2", "It's starting to spread to another vehicle now!")
            ]
        }
        
        # Select scenario
        if scenario_type is None or scenario_type not in scenarios:
            scenario_type = random.choice(list(scenarios.keys()))
        
        scenario = scenarios[scenario_type]
        
        print(f"\nSimulating {scenario_type} emergency scenario...")
        
        # Add some randomness to the scenario
        if random.random() < 0.3:  # 30% chance to modify the scenario slightly
            # Add an additional detail from the caller
            caller_extra = ("Speaker 2", "I also hear crackling sounds and there's a lot of smoke.")
            scenario.insert(random.randint(2, len(scenario)-1), caller_extra)
        
        # Process the scenario
        conversation = []
        for speaker, text in scenario:
            transcript = f"{speaker}: {text}"
            print(f"\nTRANSCRIPT: {transcript}")
            
            # Pause to simulate real-time
            time.sleep(random.uniform(1, 3))
            
            # Process with the interpreter
            result = self.interpreter.process_transcript(transcript)
            
            if result:
                # Add to conversation log
                conversation.append({
                    "transcript": transcript,
                    "interpretation": result
                })
        
        # Save scenario results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        scenario_file = f"{self.output_dir}/scenario_{scenario_type}_{timestamp}.json"
        with open(scenario_file, 'w') as f:
            json.dump({
                "scenario_type": scenario_type,
                "conversation": conversation
            }, f, indent=2)
        
        print("\nScenario simulation complete!")
        print(f"Results saved to {scenario_file}")


# Run a simple demo when the script is executed directly
if __name__ == "__main__":
    simulator = AudioSimulator()
    
    # Run a 30-second general simulation
    simulator.simulate_conversation(duration_seconds=30, avg_transcript_interval=3)
    
    # Run a specific scenario simulation
    simulator.simulate_emergency_scenario(scenario_type="kitchen_fire") 
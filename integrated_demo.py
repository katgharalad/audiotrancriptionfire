import argparse
import sys
import time
import os
import json
from threading import Thread

# Import our components
from interpret_function import interpret_transcript
from main import AudioTranscriptInterpreter
from dispatcher_router import IncidentRouter
from audio_simulator import AudioSimulator
from test_detailed_metrics import perform_metrics_test
from visualize_results import visualize_test_results
from test_enhanced_features import run_tests

def run_test_suite():
    """Run comprehensive tests of the entire system."""
    print("Running comprehensive test suite...")
    metrics = perform_metrics_test()
    return metrics

def run_enhanced_features_test():
    """Run tests specifically for the enhanced features."""
    print("Running tests for enhanced features...")
    
    # Run the enhanced features tests
    results = run_tests()
    
    # Save results to a file
    os.makedirs("test_outputs/enhanced", exist_ok=True)
    with open("test_outputs/enhanced/enhanced_features_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nEnhanced feature tests completed. Results saved to test_outputs/enhanced/enhanced_features_results.json")
    
    return results

def run_audio_simulation(duration=60, interval=5, scenario=None):
    """Run an audio simulation."""
    print(f"Starting audio simulation (duration: {duration}s, interval: {interval}s)")
    simulator = AudioSimulator(output_dir="demo_outputs/audio_simulation")
    
    if scenario:
        print(f"Simulating specific scenario: {scenario}")
        simulator.simulate_emergency_scenario(scenario_type=scenario)
    else:
        simulator.simulate_conversation(duration_seconds=duration, avg_transcript_interval=interval)

def run_dispatcher_demo():
    """Run a demo of the dispatcher router."""
    print("Starting dispatcher router demo...")
    router = IncidentRouter()
    
    # Create some test interpretations
    test_interpretations = [
        {
            "incident_type": "kitchen fire",
            "address": "123 Oak Street",
            "casualties": "none",
            "timestamp": "2023-04-01T12:34:56",
            "transcript": "Speaker 2: There's a kitchen fire at 123 Oak Street. No one is hurt."
        },
        {
            "incident_type": "structure fire",
            "address": "456 Elm Road",
            "casualties": "children trapped",
            "timestamp": "2023-04-01T12:36:12",
            "transcript": "Speaker 2: There's a house on fire at 456 Elm Road. There are children trapped inside."
        },
        {
            "incident_type": "gas leak",
            "address": "789 Pine Avenue",
            "casualties": "caller escaped alone",
            "timestamp": "2023-04-01T12:38:30",
            "transcript": "Speaker 2: I smell gas at 789 Pine Avenue. I got out but my house is full of gas."
        },
        {
            "incident_type": "vehicle fire",
            "address": "101 Maple Drive",
            "casualties": "caller trapped",
            "timestamp": "2023-04-01T12:40:45",
            "transcript": "Speaker 2: My car is on fire at 101 Maple Drive. I'm trapped inside!"
        },
        {
            "incident_type": "wildfire",
            "address": "202 Forest Lane",
            "casualties": "pets inside",
            "timestamp": "2023-04-01T12:42:15",
            "transcript": "Speaker 2: There's a wildfire near 202 Forest Lane. My pets are still in the house."
        }
    ]
    
    # Create output directory
    os.makedirs("demo_outputs/dispatcher", exist_ok=True)
    
    # Route each interpretation
    results = []
    print("\nRouting test interpretations...")
    for interp in test_interpretations:
        result = router.route(interp)
        results.append(result)
        # Simulate processing time
        time.sleep(0.5)
    
    # Save results
    with open("demo_outputs/dispatcher/routing_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Dispatcher demo complete. Results saved to demo_outputs/dispatcher/routing_results.json")

def run_gui_demo():
    """Launch the real-time GUI."""
    print("Launching real-time GUI...")
    try:
        import tkinter as tk
        from real_time_gui import FireDispatchGUI
        
        root = tk.Tk()
        app = FireDispatchGUI(root)
        
        # Start the GUI main loop
        root.mainloop()
    except ImportError:
        print("ERROR: tkinter not available. Cannot launch GUI.")
        print("To install tkinter, run: sudo apt-get install python3-tk (Linux) or use python.org installer (Windows/Mac)")

def run_interpreter_demo():
    """Run a simple demo of the interpreter."""
    print("Running interpreter demo...")
    interpreter = AudioTranscriptInterpreter(output_dir="demo_outputs/interpreter")
    
    test_transcripts = [
        "Speaker 1: This is the dispatcher. What's your emergency?",
        "Speaker 2: There's a kitchen fire at 123 Oak Street. My wife is trapped in the bathroom.",
        "Speaker 1: Is there smoke or flames visible?",
        "Speaker 2: Yes, flames are coming from the stove and spreading to the cabinets.",
        "Speaker 3: I can confirm there's a structure fire at this address.",
        "Speaker 2: The fire is getting worse. Please hurry!"
    ]
    
    for transcript in test_transcripts:
        interpreter.process_transcript(transcript)
        time.sleep(1)
    
    print("Interpreter demo complete. Results saved to demo_outputs/interpreter/")

def run_visualization():
    """Run visualization of test results and generate charts."""
    print("Generating visualizations of test results...")
    visualize_test_results()
    print("Visualizations complete!")

def main():
    """Main entry point for the integrated demo."""
    parser = argparse.ArgumentParser(description="AudioTranscripY ML Interpretation Demo")
    parser.add_argument("--mode", choices=["all", "audio", "gui", "router", "interpreter", "test", "visualize", "enhanced"], 
                      default="all", help="Demo mode to run")
    parser.add_argument("--duration", type=int, default=30, 
                      help="Duration for audio simulation (seconds)")
    parser.add_argument("--interval", type=int, default=3, 
                      help="Average interval between transcripts (seconds)")
    parser.add_argument("--scenario", choices=["kitchen_fire", "gas_leak", "vehicle_fire"],
                      help="Specific scenario to simulate")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs("demo_outputs", exist_ok=True)
    
    if args.mode == "all":
        print("Running full integrated demo...")
        
        # Run Router demo
        router_thread = Thread(target=run_dispatcher_demo)
        router_thread.start()
        
        # Run interpreter demo
        interpreter_thread = Thread(target=run_interpreter_demo)
        interpreter_thread.start()
        
        # Wait for both to complete
        router_thread.join()
        interpreter_thread.join()
        
        # Run audio simulation
        audio_thread = Thread(target=run_audio_simulation, 
                           args=(args.duration, args.interval, args.scenario))
        audio_thread.start()
        audio_thread.join()
        
        # Run test suite
        run_test_suite()
        
        # Run enhanced features test
        run_enhanced_features_test()
        
        # Generate visualizations
        run_visualization()
        
        # Finally, launch GUI (main thread)
        run_gui_demo()
    
    elif args.mode == "audio":
        run_audio_simulation(args.duration, args.interval, args.scenario)
    
    elif args.mode == "gui":
        run_gui_demo()
    
    elif args.mode == "router":
        run_dispatcher_demo()
    
    elif args.mode == "interpreter":
        run_interpreter_demo()
    
    elif args.mode == "test":
        run_test_suite()
    
    elif args.mode == "visualize":
        run_visualization()
        
    elif args.mode == "enhanced":
        run_enhanced_features_test()
    
    print("Demo completed!")

if __name__ == "__main__":
    main() 
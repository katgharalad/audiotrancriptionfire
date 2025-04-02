
import os
import sys
import json

# Add the project root directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

try:
    from dispatcher_router import IncidentRouter
except ModuleNotFoundError as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Get the input file path from command line
input_file = sys.argv[1]
output_file = sys.argv[2]

# Read the interpretation
with open(input_file, 'r') as f:
    interpretation = json.load(f)

print(f"Routing incident: {interpretation}")

# Route the incident
try:
    router = IncidentRouter()
    routing_result = router.route(interpretation)
    
    # Save the result
    with open(output_file, 'w') as f:
        json.dump(routing_result, f, indent=2)
    
    print("Routing completed successfully.")
except Exception as e:
    print(f"Error during routing: {e}")
    # Create an empty result file
    with open(output_file, 'w') as f:
        json.dump({}, f)

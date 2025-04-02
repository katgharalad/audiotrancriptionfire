import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter

def visualize_test_results():
    """Visualize and analyze the test results."""
    # Set up paths
    test_output_dir = "test_outputs"
    metrics_file = os.path.join(test_output_dir, "metrics_summary.json")
    address_file = os.path.join(test_output_dir, "address_extraction_results.json")
    
    # Create output directory for visualizations
    vis_dir = "visualizations"
    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)
    
    # Load metrics data
    print("Loading test metrics...")
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    # Print summary metrics
    print("\n----- PERFORMANCE METRICS SUMMARY -----")
    print(f"Test set size: {metrics['test_set_size']} samples")
    print(f"Average prediction time: {metrics['latency']['average_prediction_time_ms']:.4f} ms")
    
    print("\nIncident Type Classification:")
    print(f"  Accuracy: {metrics['incident_type_classification']['accuracy']:.4f}")
    print(f"  F1 Score: {metrics['incident_type_classification']['f1_score']:.4f}")
    
    print("\nCasualties Classification:")
    print(f"  Accuracy: {metrics['casualties_classification']['accuracy']:.4f}")
    print(f"  F1 Score: {metrics['casualties_classification']['f1_score']:.4f}")
    
    # Create bar chart for metrics
    plt.figure(figsize=(10, 6))
    metrics_df = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
        'Incident Type': [
            metrics['incident_type_classification']['accuracy'],
            metrics['incident_type_classification']['precision'],
            metrics['incident_type_classification']['recall'],
            metrics['incident_type_classification']['f1_score']
        ],
        'Casualties': [
            metrics['casualties_classification']['accuracy'],
            metrics['casualties_classification']['precision'],
            metrics['casualties_classification']['recall'],
            metrics['casualties_classification']['f1_score']
        ]
    })
    
    # Melt the dataframe for easier plotting
    metrics_df_melted = pd.melt(
        metrics_df, 
        id_vars=['Metric'],
        value_vars=['Incident Type', 'Casualties'],
        var_name='Classification Task', 
        value_name='Score'
    )
    
    # Create the bar chart
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Metric', y='Score', hue='Classification Task', data=metrics_df_melted)
    plt.title('Classification Performance Metrics')
    plt.ylim(0, 1.05)  # Set y-axis limit
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(f"{vis_dir}/classification_metrics.png")
    
    # Load address extraction results
    print("\n----- ADDRESS EXTRACTION ANALYSIS -----")
    try:
        with open(address_file, 'r') as f:
            address_results = json.load(f)
        
        # Analyze address extraction quality
        address_success = 0
        for result in address_results:
            address = result['extracted_address']
            if address and address.lower() != "unknown address":
                address_success += 1
                print(f"Successful extraction: {address}")
            else:
                print(f"Failed extraction: {result['transcript']}")
        
        success_rate = address_success / len(address_results) if address_results else 0
        print(f"\nAddress extraction success rate: {success_rate:.2%}")
        
        # Create a pie chart for address extraction
        plt.figure(figsize=(8, 8))
        plt.pie(
            [address_success, len(address_results) - address_success],
            labels=['Successful', 'Failed'],
            autopct='%1.1f%%',
            colors=['#66b3ff', '#ff9999'],
            startangle=90
        )
        plt.title('Address Extraction Success Rate')
        plt.savefig(f"{vis_dir}/address_extraction.png")
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not analyze address extraction: {e}")
    
    # Load and analyze simulation data
    print("\n----- SIMULATION DATA ANALYSIS -----")
    simulation_dir = "audio_simulation"
    if os.path.exists(simulation_dir):
        # Find the most recent simulation file
        simulation_files = [f for f in os.listdir(simulation_dir) if f.startswith("simulation_")]
        if simulation_files:
            latest_sim = max(simulation_files)
            sim_path = os.path.join(simulation_dir, latest_sim)
            
            try:
                with open(sim_path, 'r') as f:
                    sim_data = json.load(f)
                
                # Print simulation metrics
                metrics = sim_data.get('metrics', {})
                print(f"Total transcripts: {metrics.get('total_transcripts', 0)}")
                print(f"Caller transcripts: {metrics.get('caller_transcripts', 0)}")
                print(f"Interpretations generated: {metrics.get('interpretations_generated', 0)}")
                print(f"Average interpretation time: {metrics.get('avg_interpretation_time', 0)*1000:.2f} ms")
                
                # Plot conversation flow
                conversation = sim_data.get('conversation', [])
                if conversation:
                    # Extract timestamps and incident types
                    timestamps = [entry.get('timestamp', 0) for entry in conversation]
                    incident_types = [entry.get('interpretation', {}).get('incident_type', 'unknown') 
                                     for entry in conversation]
                    
                    # Create a timeline plot
                    plt.figure(figsize=(12, 6))
                    incident_type_set = sorted(set(incident_types))
                    colors = plt.cm.tab10(np.linspace(0, 1, len(incident_type_set)))
                    color_map = dict(zip(incident_type_set, colors))
                    
                    for i, (ts, incident) in enumerate(zip(timestamps, incident_types)):
                        plt.scatter(ts, 1, color=color_map[incident], s=100, zorder=2)
                        plt.text(ts, 1.1, incident, rotation=45, ha='right', fontsize=8)
                    
                    plt.yticks([])
                    plt.xlabel('Time (seconds)')
                    plt.title('Conversation Timeline with Incident Types')
                    plt.grid(axis='x', linestyle='--', alpha=0.7)
                    
                    # Add legend
                    for incident, color in color_map.items():
                        plt.scatter([], [], color=color, label=incident)
                    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
                    
                    plt.tight_layout()
                    plt.savefig(f"{vis_dir}/conversation_timeline.png")
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error analyzing simulation data: {e}")
    else:
        print("No simulation data found.")
    
    # Analyze dispatcher routing data
    print("\n----- DISPATCHER ROUTING ANALYSIS -----")
    dispatch_dir = "demo_outputs/dispatcher"
    routing_file = os.path.join(dispatch_dir, "routing_results.json")
    
    if os.path.exists(routing_file):
        try:
            with open(routing_file, 'r') as f:
                routing_results = json.load(f)
            
            # Collect statistics
            handlers = [result.get('handler', 'unknown') for result in routing_results]
            priorities = [result.get('interpretation', {}).get('priority_level', 'unknown') 
                         for result in routing_results]
            resources_used = []
            for result in routing_results:
                resources_used.extend(result.get('resources', []))
            
            # Count frequencies
            handler_counts = Counter(handlers)
            priority_counts = Counter(priorities)
            resource_counts = Counter(resources_used)
            
            # Print statistics
            print("Handlers used:")
            for handler, count in handler_counts.most_common():
                print(f"  - {handler}: {count}")
            
            print("\nPriority levels:")
            for priority, count in priority_counts.most_common():
                print(f"  - {priority}: {count}")
            
            print("\nResources dispatched:")
            for resource, count in resource_counts.most_common():
                print(f"  - {resource}: {count}")
            
            # Create charts for dispatcher statistics
            # Priority pie chart
            plt.figure(figsize=(8, 8))
            priority_colors = {
                'CRITICAL': '#ff0000',  # Red
                'URGENT': '#ff9900',    # Orange
                'HIGH': '#ffcc00',      # Yellow
                'MEDIUM': '#66cc00',    # Green
                'LOW': '#0099cc'        # Blue
            }
            
            # Convert to percentages
            priority_data = [(p, c/len(routing_results)*100) for p, c in priority_counts.items()]
            priority_data.sort(key=lambda x: {
                'CRITICAL': 5, 'URGENT': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1
            }.get(x[0], 0), reverse=True)
            
            plt.pie(
                [d[1] for d in priority_data],
                labels=[d[0] for d in priority_data],
                autopct='%1.1f%%',
                colors=[priority_colors.get(p[0], '#999999') for p in priority_data],
                startangle=90
            )
            plt.title('Incident Priority Levels')
            plt.savefig(f"{vis_dir}/priority_levels.png")
            
            # Resources bar chart
            plt.figure(figsize=(10, 6))
            resource_df = pd.DataFrame(list(resource_counts.items()), 
                                      columns=['Resource', 'Count'])
            resource_df = resource_df.sort_values('Count', ascending=False)
            
            sns.barplot(x='Resource', y='Count', data=resource_df)
            plt.title('Resources Dispatched')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{vis_dir}/resources_dispatched.png")
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error analyzing dispatcher data: {e}")
    else:
        print("No dispatcher routing data found.")
    
    print(f"\nVisualizations saved to {vis_dir}/ directory")
    return True

if __name__ == "__main__":
    visualize_test_results() 
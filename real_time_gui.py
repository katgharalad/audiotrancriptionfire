import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import json
import time
import datetime
import random
import os
from typing import Dict, List, Optional

from interpret_function import interpret_transcript
from dispatcher_router import IncidentRouter

class FireDispatchGUI:
    """
    Real-time GUI for visualizing emergency incident interpretations
    and dispatch responses.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Fire Dispatch ML Interpretation System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Queue for thread-safe communication
        self.queue = queue.Queue()
        
        # Initialize components
        self.setup_ui()
        
        # Initialize router
        self.router = IncidentRouter()
        
        # State tracking
        self.current_incidents = {}
        self.verification_queue = []
        self.active_units = {
            "fire_engine": ["Engine 101", "Engine 102", "Engine 103"],
            "ladder_truck": ["Ladder 201", "Ladder 202"],
            "ambulance": ["Medic 301", "Medic 302", "Medic 303", "Medic 304"],
            "battalion_chief": ["Battalion 1"],
            "hazmat_unit": ["Hazmat 401"],
            "utility_company": ["Utility 501"],
            "brush_units": ["Brush 601", "Brush 602"],
            "water_tenders": ["Tender 701", "Tender 702"],
            "air_support": ["Air 801"],
            "single_unit": []  # Will use an engine for this
        }
        self.dispatched_units = {}
        
        # Start processing thread
        self.running = True
        self.process_thread = threading.Thread(target=self.process_queue)
        self.process_thread.daemon = True
        self.process_thread.start()
        
        # Auto-update UI
        self.root.after(100, self.update_ui)
    
    def setup_ui(self):
        """Set up the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="DELAWARE, OH FIRE DEPARTMENT", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(main_frame, text="Real-Time Dispatch Interpretation System", font=("Arial", 12))
        subtitle_label.pack(pady=5)
        
        # Horizontal split
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel - Incident list and input
        left_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(left_frame, weight=2)
        
        # Input section
        input_frame = ttk.LabelFrame(left_frame, text="Transcript Input", padding=5)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.transcript_entry = ttk.Entry(input_frame, width=50)
        self.transcript_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.transcript_entry.bind("<Return>", self.on_submit_transcript)
        
        submit_button = ttk.Button(input_frame, text="Process", command=self.on_submit_transcript)
        submit_button.pack(side=tk.RIGHT, padx=5)
        
        # Preset speaker buttons
        speaker_frame = ttk.Frame(left_frame)
        speaker_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speaker_frame, text="Speaker:").pack(side=tk.LEFT, padx=5)
        
        for speaker in ["Speaker 1", "Speaker 2", "Speaker 3", "Speaker 4"]:
            btn = ttk.Button(speaker_frame, text=speaker, 
                            command=lambda s=speaker: self.set_speaker(s))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Active incidents section
        incidents_frame = ttk.LabelFrame(left_frame, text="Active Incidents", padding=5)
        incidents_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add notebook for tabbed view
        incidents_notebook = ttk.Notebook(incidents_frame)
        incidents_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Incidents tab
        incidents_tab = ttk.Frame(incidents_notebook)
        incidents_notebook.add(incidents_tab, text="Incidents")
        
        self.incidents_tree = ttk.Treeview(incidents_tab, columns=("priority", "address", "type"), show="headings")
        self.incidents_tree.heading("priority", text="Priority")
        self.incidents_tree.heading("address", text="Address")
        self.incidents_tree.heading("type", text="Type")
        self.incidents_tree.column("priority", width=80)
        self.incidents_tree.column("address", width=200)
        self.incidents_tree.column("type", width=120)
        self.incidents_tree.pack(fill=tk.BOTH, expand=True)
        self.incidents_tree.bind("<Double-1>", self.on_incident_selected)
        
        # Verification tab
        verification_tab = ttk.Frame(incidents_notebook)
        incidents_notebook.add(verification_tab, text="Needs Verification")
        
        self.verification_tree = ttk.Treeview(verification_tab, columns=("confidence", "address", "type"), show="headings")
        self.verification_tree.heading("confidence", text="Confidence")
        self.verification_tree.heading("address", text="Address")
        self.verification_tree.heading("type", text="Type")
        self.verification_tree.column("confidence", width=80)
        self.verification_tree.column("address", width=200)
        self.verification_tree.column("type", width=120)
        self.verification_tree.pack(fill=tk.BOTH, expand=True)
        self.verification_tree.bind("<Double-1>", self.on_verification_selected)
        
        # Right panel - Incident details and map
        right_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(right_frame, weight=3)
        
        # Incident details section
        self.details_frame = ttk.LabelFrame(right_frame, text="Incident Details", padding=10)
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Mock map image
        self.map_canvas = tk.Canvas(self.details_frame, bg="#e0e0e0", height=300)
        self.map_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        self.map_canvas.create_text(400, 150, text="DELAWARE, OH MAP", font=("Arial", 18, "bold"), fill="#666666")
        
        # Incident details text
        self.details_text = scrolledtext.ScrolledText(self.details_frame, height=15)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        # Dispatch log section
        log_frame = ttk.LabelFrame(right_frame, text="Dispatch Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("System Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    def set_speaker(self, speaker):
        """Set the speaker prefix in the transcript entry."""
        text = self.transcript_entry.get()
        if ":" in text:
            text = text.split(":", 1)[1].strip()
        
        self.transcript_entry.delete(0, tk.END)
        self.transcript_entry.insert(0, f"{speaker}: {text}")
    
    def on_submit_transcript(self, event=None):
        """Process the submitted transcript."""
        transcript = self.transcript_entry.get().strip()
        if not transcript:
            return
        
        # Ensure there's a speaker prefix
        if ":" not in transcript:
            transcript = f"Speaker 2: {transcript}"
        
        # Add to log
        self.add_to_log(f"TRANSCRIPT: {transcript}")
        
        # Process in background thread
        self.queue.put(("process_transcript", transcript))
        
        # Clear entry
        self.transcript_entry.delete(0, tk.END)
    
    def on_incident_selected(self, event=None):
        """Display details for the selected incident."""
        selected_id = self.incidents_tree.selection()
        if not selected_id:
            return
        
        incident_id = selected_id[0]
        if incident_id in self.current_incidents:
            incident = self.current_incidents[incident_id]
            self.display_incident_details(incident)
    
    def on_verification_selected(self, event=None):
        """Display details for the selected verification item."""
        selected_id = self.verification_tree.selection()
        if not selected_id:
            return
        
        item_id = selected_id[0]
        index = int(item_id.split('_')[1])
        
        if 0 <= index < len(self.verification_queue):
            interpretation = self.verification_queue[index]
            
            # Create a detailed view of the interpretation
            details = (
                f"INCIDENT TYPE: {interpretation.get('incident_type', '').upper()}\n"
                f"CONFIDENCE: {interpretation.get('incident_type_confidence', 0.0):.2f}\n\n"
                f"ADDRESS: {interpretation.get('address', '')}\n"
            )
            
            # Add address validation if available
            if 'address_validation' in interpretation:
                valid = interpretation['address_validation'].get('valid', False)
                conf = interpretation['address_validation'].get('confidence', 0.0)
                details += f"ADDRESS VALID: {valid} (Confidence: {conf:.2f})\n\n"
            
            details += f"CASUALTIES: {interpretation.get('casualties', '')}\n"
            
            # Add structured casualties if available
            if 'casualties_structured' in interpretation:
                struct = interpretation['casualties_structured']
                details += "AFFECTED: "
                categories = []
                if struct.get('children', False): categories.append("Children")
                if struct.get('elderly', False): categories.append("Elderly")
                if struct.get('pets', False): categories.append("Pets")
                if struct.get('caller', False): categories.append("Caller")
                details += ", ".join(categories) if categories else "None"
                details += "\n\n"
            
            # Add priority information
            if 'priority' in interpretation and 'priority_level' in interpretation:
                details += f"PRIORITY: {interpretation.get('priority_level', '')} ({interpretation.get('priority', '')})\n\n"
            
            details += f"VERIFICATION NEEDED BECAUSE:\n"
            
            if interpretation.get('incident_type_confidence', 1.0) < 0.7:
                details += f"- Low confidence in incident type: {interpretation.get('incident_type_confidence', 0.0):.2f}\n"
            
            if interpretation.get('casualties_confidence', 1.0) < 0.7:
                details += f"- Low confidence in casualties: {interpretation.get('casualties_confidence', 0.0):.2f}\n"
            
            if 'address_validation' in interpretation and interpretation['address_validation'].get('needs_verification', False):
                details += f"- Address needs verification (confidence: {interpretation['address_validation'].get('confidence', 0.0):.2f})\n"
            
            details += f"\nTRANSCRIPT: {interpretation.get('transcript', '')}\n"
            
            # Add manual verification buttons
            details += "\nAFTER VERIFICATION: Use the buttons below to dispatch or reject."
            
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, details)
            self.details_text.config(state=tk.DISABLED)
            
            # Add verification action buttons
            verify_frame = ttk.Frame(self.details_frame)
            verify_frame.pack(fill=tk.X, pady=10)
            
            # Approve button
            approve_btn = ttk.Button(
                verify_frame, 
                text="Verify & Dispatch", 
                command=lambda: self.verify_and_dispatch(index)
            )
            approve_btn.pack(side=tk.LEFT, padx=5)
            
            # Edit button
            edit_btn = ttk.Button(
                verify_frame, 
                text="Edit & Dispatch", 
                command=lambda: self.edit_interpretation(index)
            )
            edit_btn.pack(side=tk.LEFT, padx=5)
            
            # Reject button
            reject_btn = ttk.Button(
                verify_frame, 
                text="Reject", 
                command=lambda: self.reject_interpretation(index)
            )
            reject_btn.pack(side=tk.LEFT, padx=5)
    
    def verify_and_dispatch(self, index):
        """Verify and dispatch an interpretation from the verification queue."""
        if 0 <= index < len(self.verification_queue):
            interpretation = self.verification_queue[index]
            
            # Mark as verified
            interpretation['needs_verification'] = False
            
            # Route through the incident router
            routing_result = self.router.route(interpretation)
            
            # Add to incidents
            incident_id = f"incident_{int(time.time())}"
            self.current_incidents[incident_id] = routing_result
            
            # Simulate unit dispatch
            self.dispatch_units(incident_id, routing_result)
            
            # Remove from verification queue
            self.verification_queue.pop(index)
            
            # Clear details and refresh UI
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.config(state=tk.DISABLED)
            
            # Remove verification buttons
            for widget in self.details_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget != self.details_text:
                    widget.destroy()
            
            self.add_to_log(f"VERIFIED AND DISPATCHED: {interpretation['incident_type']} at {interpretation['address']}")
    
    def edit_interpretation(self, index):
        """Edit the interpretation before dispatching."""
        if 0 <= index < len(self.verification_queue):
            interpretation = self.verification_queue[index]
            
            # Create a simple edit dialog
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Interpretation")
            edit_window.geometry("500x400")
            
            # Edit fields
            ttk.Label(edit_window, text="Incident Type:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            incident_type_entry = ttk.Entry(edit_window, width=40)
            incident_type_entry.insert(0, interpretation.get('incident_type', ''))
            incident_type_entry.grid(row=0, column=1, padx=10, pady=5)
            
            ttk.Label(edit_window, text="Address:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            address_entry = ttk.Entry(edit_window, width=40)
            address_entry.insert(0, interpretation.get('address', ''))
            address_entry.grid(row=1, column=1, padx=10, pady=5)
            
            ttk.Label(edit_window, text="Casualties:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            casualties_entry = ttk.Entry(edit_window, width=40)
            casualties_entry.insert(0, interpretation.get('casualties', ''))
            casualties_entry.grid(row=2, column=1, padx=10, pady=5)
            
            ttk.Label(edit_window, text="Priority (1-5):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
            priority_entry = ttk.Entry(edit_window, width=40)
            priority_entry.insert(0, str(interpretation.get('priority', 3.0)))
            priority_entry.grid(row=3, column=1, padx=10, pady=5)
            
            # Structured casualties checkboxes
            ttk.Label(edit_window, text="Affected:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            
            casualties_frame = ttk.Frame(edit_window)
            casualties_frame.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
            
            children_var = tk.BooleanVar(value=interpretation.get('casualties_structured', {}).get('children', False))
            children_check = ttk.Checkbutton(casualties_frame, text="Children", variable=children_var)
            children_check.grid(row=0, column=0, padx=5)
            
            elderly_var = tk.BooleanVar(value=interpretation.get('casualties_structured', {}).get('elderly', False))
            elderly_check = ttk.Checkbutton(casualties_frame, text="Elderly", variable=elderly_var)
            elderly_check.grid(row=0, column=1, padx=5)
            
            pets_var = tk.BooleanVar(value=interpretation.get('casualties_structured', {}).get('pets', False))
            pets_check = ttk.Checkbutton(casualties_frame, text="Pets", variable=pets_var)
            pets_check.grid(row=0, column=2, padx=5)
            
            caller_var = tk.BooleanVar(value=interpretation.get('casualties_structured', {}).get('caller', False))
            caller_check = ttk.Checkbutton(casualties_frame, text="Caller", variable=caller_var)
            caller_check.grid(row=0, column=3, padx=5)
            
            # Save button
            def save_and_dispatch():
                # Update interpretation
                interpretation['incident_type'] = incident_type_entry.get()
                interpretation['address'] = address_entry.get()
                interpretation['casualties'] = casualties_entry.get()
                
                try:
                    interpretation['priority'] = float(priority_entry.get())
                except ValueError:
                    pass
                
                # Update structured casualties
                if 'casualties_structured' not in interpretation:
                    interpretation['casualties_structured'] = {}
                
                interpretation['casualties_structured']['children'] = children_var.get()
                interpretation['casualties_structured']['elderly'] = elderly_var.get()
                interpretation['casualties_structured']['pets'] = pets_var.get()
                interpretation['casualties_structured']['caller'] = caller_var.get()
                
                # Mark as verified
                interpretation['needs_verification'] = False
                
                # Close dialog
                edit_window.destroy()
                
                # Dispatch
                self.verify_and_dispatch(index)
            
            save_btn = ttk.Button(edit_window, text="Save & Dispatch", command=save_and_dispatch)
            save_btn.grid(row=5, column=0, columnspan=2, pady=20)
    
    def reject_interpretation(self, index):
        """Reject an interpretation from the verification queue."""
        if 0 <= index < len(self.verification_queue):
            interpretation = self.verification_queue[index]
            
            # Remove from verification queue
            self.verification_queue.pop(index)
            
            # Clear details and refresh UI
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.config(state=tk.DISABLED)
            
            # Remove verification buttons
            for widget in self.details_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget != self.details_text:
                    widget.destroy()
            
            self.add_to_log(f"REJECTED: {interpretation['incident_type']} at {interpretation['address']}")
    
    def process_queue(self):
        """Background thread to process the queue."""
        while self.running:
            try:
                action, data = self.queue.get(block=False)
                
                if action == "process_transcript":
                    # Process the transcript
                    interpretation = interpret_transcript(data)
                    
                    if interpretation:
                        # Check if it needs verification
                        if interpretation.get('needs_verification', False):
                            self.verification_queue.append(interpretation)
                            self.add_to_log(f"ADDED TO VERIFICATION: {interpretation['incident_type']} at {interpretation['address']}")
                        
                        # Route through the incident router
                        routing_result = self.router.route(interpretation)
                        
                        # Add to incidents
                        incident_id = f"incident_{int(time.time())}"
                        self.current_incidents[incident_id] = routing_result
                        
                        # Simulate unit dispatch
                        self.dispatch_units(incident_id, routing_result)
                
                self.queue.task_done()
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in process_queue: {e}")
                time.sleep(0.1)
    
    def update_ui(self):
        """Update the UI with current incidents."""
        try:
            # Update incidents tree
            self.incidents_tree.delete(*self.incidents_tree.get_children())
            
            for incident_id, incident in self.current_incidents.items():
                interp = incident.get("interpretation", {})
                priority = interp.get("priority_level", "")
                address = interp.get("address", "")
                incident_type = interp.get("incident_type", "")
                
                # Set color tag based on priority
                priority_color = self.get_priority_color(priority)
                
                self.incidents_tree.insert("", tk.END, incident_id, values=(priority, address, incident_type), 
                                        tags=(priority_color,))
            
            # Configure tags
            self.incidents_tree.tag_configure("critical", background="#ffcccc")
            self.incidents_tree.tag_configure("urgent", background="#ffffcc")
            self.incidents_tree.tag_configure("high", background="#e6f2ff")
            self.incidents_tree.tag_configure("medium", background="#e6ffe6")
            self.incidents_tree.tag_configure("low", background="#f2f2f2")
            
            # Update verification tree
            self.verification_tree.delete(*self.verification_tree.get_children())
            
            for i, interp in enumerate(self.verification_queue):
                item_id = f"verify_{i}"
                confidence = interp.get("confidence", 0.0)
                address = interp.get("address", "")
                incident_type = interp.get("incident_type", "")
                
                # Set color tag based on confidence
                confidence_color = "low_conf" if confidence < 0.7 else "medium_conf"
                
                self.verification_tree.insert("", tk.END, item_id, 
                                            values=(f"{confidence:.2f}", address, incident_type), 
                                            tags=(confidence_color,))
            
            # Configure verification tags
            self.verification_tree.tag_configure("low_conf", background="#ffcccc")
            self.verification_tree.tag_configure("medium_conf", background="#ffffcc")
            
            # Draw incidents on map (mock)
            self.update_map()
            
        except Exception as e:
            print(f"Error in update_ui: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def get_priority_color(self, priority):
        """Get the color tag for a priority level."""
        if priority == "CRITICAL":
            return "critical"
        elif priority == "URGENT":
            return "urgent"
        elif priority == "HIGH":
            return "high"
        elif priority == "MEDIUM":
            return "medium"
        else:
            return "low"
    
    def update_map(self):
        """Update the map canvas with incident markers."""
        self.map_canvas.delete("incident")
        
        for incident_id, incident in self.current_incidents.items():
            interp = incident.get("interpretation", {})
            
            # Generate random position (mock)
            x = random.randint(50, 750)
            y = random.randint(50, 250)
            
            # Determine marker color based on incident type
            incident_type = interp.get("incident_type", "").lower()
            if "fire" in incident_type:
                color = "red"
            elif "gas" in incident_type:
                color = "yellow"
            else:
                color = "blue"
            
            # Draw marker
            self.map_canvas.create_oval(x-10, y-10, x+10, y+10, fill=color, tags=("incident", incident_id))
            self.map_canvas.create_text(x, y-20, text=interp.get("address", ""), tags=("incident", incident_id))
    
    def display_incident_details(self, incident):
        """Display details for a selected incident."""
        interp = incident.get("interpretation", {})
        resources = incident.get("resources", [])
        
        details = (
            f"INCIDENT TYPE: {interp.get('incident_type', '').upper()}\n"
        )
        
        # Add confidence if available
        if 'incident_type_confidence' in interp:
            details += f"CONFIDENCE: {interp.get('incident_type_confidence', 0.0):.2f}\n"
        
        details += f"\nADDRESS: {interp.get('address', '')}\n"
        
        # Add address validation if available
        if 'address_validation' in interp:
            valid = interp['address_validation'].get('valid', False)
            conf = interp['address_validation'].get('confidence', 0.0)
            details += f"ADDRESS VALID: {valid} (Confidence: {conf:.2f})\n"
        
        details += f"\nCASUALTIES: {interp.get('casualties', '')}\n"
        
        # Add structured casualties if available
        if 'casualties_structured' in interp:
            struct = interp['casualties_structured']
            details += "AFFECTED: "
            categories = []
            if struct.get('children', False): categories.append("Children")
            if struct.get('elderly', False): categories.append("Elderly")
            if struct.get('pets', False): categories.append("Pets")
            if struct.get('caller', False): categories.append("Caller")
            details += ", ".join(categories) if categories else "None"
            details += "\n"
        
        # Add priority information
        if 'priority' in interp and 'priority_level' in interp:
            details += f"\nPRIORITY: {interp.get('priority_level', '')} ({interp.get('priority', '')})\n"
        
        # Add verification status
        if 'needs_verification' in interp:
            verification = "REQUIRES VERIFICATION" if interp.get('needs_verification', False) else "VERIFIED"
            details += f"STATUS: {verification}\n"
        
        details += f"\nDISPATCH MESSAGE: {incident.get('message', '')}\n\n"
        details += f"RESOURCES DISPATCHED:\n"
        
        for resource in resources:
            details += f"  - {resource.upper()}\n"
        
        incident_id = next((i for i, inc in self.current_incidents.items() if inc == incident), None)
        if incident_id and incident_id in self.dispatched_units:
            details += "\nUNITS RESPONDING:\n"
            for unit in self.dispatched_units[incident_id]:
                details += f"  - {unit}\n"
        
        details += f"\nTRANSCRIPT: {interp.get('transcript', '')}\n"
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
    
    def dispatch_units(self, incident_id, incident):
        """Simulate dispatching units to an incident."""
        resources = incident.get("resources", [])
        interp = incident.get("interpretation", {})
        
        dispatched = []
        for resource_type in resources:
            available_units = [unit for unit in self.active_units.get(resource_type, []) 
                            if not any(unit in units for units in self.dispatched_units.values())]
            
            if available_units:
                unit = available_units[0]
                dispatched.append(unit)
            elif resource_type == "single_unit" and "fire_engine" in self.active_units:
                # Use an engine for single unit response if available
                available_engines = [unit for unit in self.active_units.get("fire_engine", []) 
                                if not any(unit in units for units in self.dispatched_units.values())]
                if available_engines:
                    dispatched.append(available_engines[0])
        
        if dispatched:
            self.dispatched_units[incident_id] = dispatched
            
            # Add to log
            units_str = ", ".join(dispatched)
            self.add_to_log(f"DISPATCHED: {units_str} to {interp.get('incident_type', '')} at {interp.get('address', '')}")
            
            # Update status
            self.status_var.set(f"Dispatched {len(dispatched)} units to {interp.get('address', '')}")
        else:
            self.add_to_log(f"WARNING: No units available for {interp.get('incident_type', '')} at {interp.get('address', '')}")
            self.status_var.set("No units available - Mutual Aid Requested")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FireDispatchGUI(root)
    
    # Display simulated transcript after a delay
    def simulate_transcript():
        app.transcript_entry.insert(0, "Speaker 2: There's a kitchen fire at 123 Main Street. My dog is trapped inside.")
        app.on_submit_transcript()
        
        # Schedule another transcript
        root.after(10000, lambda: app.transcript_entry.insert(0, "Speaker 2: Structure fire at 456 Oak Avenue. Children trapped upstairs."))
        root.after(10000, lambda: app.on_submit_transcript())
        
        # Schedule another transcript
        root.after(20000, lambda: app.transcript_entry.insert(0, "Speaker 2: Gas leak at 789 Pine Boulevard. Everyone evacuated."))
        root.after(20000, lambda: app.on_submit_transcript())
    
    # Schedule initial simulation
    root.after(2000, simulate_transcript)
    
    # Start the GUI main loop
    root.mainloop() 
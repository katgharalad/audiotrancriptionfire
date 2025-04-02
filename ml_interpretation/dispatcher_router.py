import os
import json
import time
import datetime
from typing import Dict, List, Callable, Any, Optional

class IncidentRouter:
    """
    A LangChain-style router for dispatching incident interpretations
    to the appropriate handler based on incident type.
    """
    def __init__(self):
        """Initialize the router with default handlers."""
        self.routes = {}
        self.default_handler = self._default_handler
        self.middleware = []
        
        # Register default handlers for common incident types
        self.register_handler("structure fire", self._structure_fire_handler)
        self.register_handler("kitchen fire", self._kitchen_fire_handler)
        self.register_handler("gas leak", self._gas_leak_handler)
        self.register_handler("vehicle fire", self._vehicle_fire_handler)
        self.register_handler("wildfire", self._wildfire_handler)
        self.register_handler("false alarm", self._false_alarm_handler)
        self.register_handler("electrical fire", self._electrical_fire_handler)
        self.register_handler("industrial fire", self._industrial_fire_handler)
        
        # Register middleware
        self.register_middleware(self._log_interpretation)
        self.register_middleware(self._priority_calculator)
        
        print("IncidentRouter initialized with default handlers and middleware")
    
    def register_handler(self, incident_type: str, handler: Callable[[Dict], Any]) -> None:
        """
        Register a handler function for a specific incident type.
        
        Args:
            incident_type (str): The type of incident to handle
            handler (Callable): The function to call when this incident type is detected
        """
        self.routes[incident_type.lower()] = handler
        print(f"Registered handler for '{incident_type}'")
    
    def register_middleware(self, middleware: Callable[[Dict], Dict]) -> None:
        """
        Register middleware to process all interpretations before they reach handlers.
        
        Args:
            middleware (Callable): Function that takes and returns an interpretation dict
        """
        self.middleware.append(middleware)
    
    def set_default_handler(self, handler: Callable[[Dict], Any]) -> None:
        """
        Set the default handler for incident types without a specific handler.
        
        Args:
            handler (Callable): The function to call for unregistered incident types
        """
        self.default_handler = handler
    
    def route(self, interpretation: Dict) -> Any:
        """
        Route an interpretation to the appropriate handler.
        
        Args:
            interpretation (Dict): The incident interpretation dict
            
        Returns:
            Any: The result from the handler
        """
        # Apply middleware
        for mw in self.middleware:
            interpretation = mw(interpretation)
        
        # Get incident type and determine handler
        incident_type = interpretation.get("incident_type", "").lower()
        handler = self.routes.get(incident_type, self.default_handler)
        
        # Call handler and return result
        return handler(interpretation)
    
    # Default middleware functions
    def _log_interpretation(self, interpretation: Dict) -> Dict:
        """Log the interpretation and return it unchanged."""
        print(f"[{datetime.datetime.now().isoformat()}] Routing interpretation: {json.dumps(interpretation)}")
        return interpretation
    
    def _priority_calculator(self, interpretation: Dict) -> Dict:
        """Add a priority level based on incident type and casualties."""
        # Base priority: 1 (lowest) to 5 (highest)
        priority_map = {
            "false alarm": 1,
            "vehicle fire": 3,
            "kitchen fire": 3,
            "electrical fire": 3,
            "industrial fire": 4,
            "gas leak": 4,
            "structure fire": 4,
            "wildfire": 5
        }
        
        # Get base priority
        base_priority = priority_map.get(interpretation.get("incident_type", "").lower(), 2)
        
        # Adjust priority based on casualties
        casualties = interpretation.get("casualties", "none").lower()
        if casualties == "none":
            priority_adjustment = 0
        elif casualties in ["caller escaped alone", "pets inside"]:
            priority_adjustment = 0.5
        elif casualties in ["caller trapped", "unknown number trapped"]:
            priority_adjustment = 1
        elif casualties in ["children trapped", "elderly person trapped"]:
            priority_adjustment = 1.5
        else:
            priority_adjustment = 0
        
        # Calculate final priority
        final_priority = min(5, base_priority + priority_adjustment)
        
        # Add priority to interpretation
        interpretation["priority"] = final_priority
        interpretation["priority_level"] = self._priority_level(final_priority)
        
        return interpretation
    
    def _priority_level(self, priority: float) -> str:
        """Convert numerical priority to a descriptive level."""
        if priority >= 4.5:
            return "CRITICAL"
        elif priority >= 3.5:
            return "URGENT"
        elif priority >= 2.5:
            return "HIGH"
        elif priority >= 1.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    # Default handlers
    def _default_handler(self, interpretation: Dict) -> Dict:
        """Default handler for unregistered incident types."""
        print(f"DEFAULT HANDLER: {interpretation.get('incident_type')} at {interpretation.get('address')}")
        return {
            "status": "processed",
            "handler": "default",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Incident processed with default handler",
            "interpretation": interpretation
        }
    
    def _structure_fire_handler(self, interpretation: Dict) -> Dict:
        """Handler for structure fires."""
        print(f"STRUCTURE FIRE: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        # In a real system, this would trigger specific protocols for structure fires
        return {
            "status": "processed",
            "handler": "structure_fire",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching fire units to structure fire",
            "resources": ["fire_engine", "ladder_truck", "ambulance", "battalion_chief"],
            "interpretation": interpretation
        }
    
    def _kitchen_fire_handler(self, interpretation: Dict) -> Dict:
        """Handler for kitchen fires."""
        print(f"KITCHEN FIRE: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "kitchen_fire",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching units to kitchen fire",
            "resources": ["fire_engine", "ambulance"],
            "interpretation": interpretation
        }
    
    def _gas_leak_handler(self, interpretation: Dict) -> Dict:
        """Handler for gas leaks."""
        print(f"GAS LEAK: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "gas_leak",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching hazmat and fire units to gas leak",
            "resources": ["fire_engine", "hazmat_unit", "utility_company"],
            "interpretation": interpretation
        }
    
    def _vehicle_fire_handler(self, interpretation: Dict) -> Dict:
        """Handler for vehicle fires."""
        print(f"VEHICLE FIRE: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "vehicle_fire",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching units to vehicle fire",
            "resources": ["fire_engine"],
            "interpretation": interpretation
        }
    
    def _wildfire_handler(self, interpretation: Dict) -> Dict:
        """Handler for wildfires."""
        print(f"WILDFIRE: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "wildfire",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching wildland fire units and requesting mutual aid",
            "resources": ["brush_units", "water_tenders", "air_support", "mutual_aid"],
            "interpretation": interpretation
        }
    
    def _false_alarm_handler(self, interpretation: Dict) -> Dict:
        """Handler for false alarms."""
        print(f"FALSE ALARM: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "false_alarm",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching single unit for investigation",
            "resources": ["single_unit"],
            "interpretation": interpretation
        }
    
    def _electrical_fire_handler(self, interpretation: Dict) -> Dict:
        """Handler for electrical fires."""
        print(f"ELECTRICAL FIRE: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "electrical_fire",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching units with electrical hazard protocols",
            "resources": ["fire_engine", "ladder_truck", "utility_company"],
            "interpretation": interpretation
        }
    
    def _industrial_fire_handler(self, interpretation: Dict) -> Dict:
        """Handler for industrial fires."""
        print(f"INDUSTRIAL FIRE: {interpretation.get('address')} - Casualties: {interpretation.get('casualties')}")
        return {
            "status": "processed",
            "handler": "industrial_fire",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Dispatching hazmat and fire units with industrial protocol",
            "resources": ["fire_engine", "hazmat_unit", "ladder_truck", "battalion_chief", "ambulance"],
            "interpretation": interpretation
        }


# Demo usage
if __name__ == "__main__":
    # Initialize the router
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
        }
    ]
    
    # Route each interpretation
    print("\nRouting test interpretations...")
    for interp in test_interpretations:
        result = router.route(interp)
        print(f"\nROUTING RESULT: {json.dumps(result, indent=2)}")
        # Simulate processing time
        time.sleep(1) 
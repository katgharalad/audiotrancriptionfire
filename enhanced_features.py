import numpy as np
import pandas as pd
import re
import json
import os
from collections import defaultdict
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Path to the Delaware addresses for validation
DELAWARE_ADDRESSES_PATH = "data/delaware_addresses.csv"

# 1. Confidence Score Implementation
def add_confidence_scores(interpretation, probabilities):
    """
    Add confidence scores to interpretation based on model probabilities.
    
    Args:
        interpretation (dict): Current interpretation
        probabilities (dict): Probabilities for each class
        
    Returns:
        dict: Enhanced interpretation with confidence scores
    """
    enhanced = interpretation.copy()
    
    # Add confidence for incident type
    if 'incident_type_proba' in probabilities:
        incident_proba = probabilities['incident_type_proba']
        incident_type = interpretation.get('incident_type', '')
        confidence = max(incident_proba) if incident_proba else 0.0
        
        enhanced['incident_type_confidence'] = round(float(confidence), 2)
        
    # Add confidence for casualties
    if 'casualties_proba' in probabilities:
        casualties_proba = probabilities['casualties_proba']
        casualties = interpretation.get('casualties', '')
        confidence = max(casualties_proba) if casualties_proba else 0.0
        
        enhanced['casualties_confidence'] = round(float(confidence), 2)
    
    # Calculate overall confidence (average of available confidences)
    confidences = []
    if 'incident_type_confidence' in enhanced:
        confidences.append(enhanced['incident_type_confidence'])
    if 'casualties_confidence' in enhanced:
        confidences.append(enhanced['casualties_confidence'])
    
    if confidences:
        enhanced['confidence'] = round(sum(confidences) / len(confidences), 2)
    
    return enhanced

def needs_verification(interpretation, threshold=0.70):
    """
    Determine if an interpretation needs human verification based on confidence.
    
    Args:
        interpretation (dict): Interpretation with confidence scores
        threshold (float): Minimum confidence threshold
        
    Returns:
        bool: True if verification needed, False otherwise
    """
    # Check if confidence is below threshold
    if 'confidence' in interpretation and interpretation['confidence'] < threshold:
        return True
    
    # Check individual confidences
    if 'incident_type_confidence' in interpretation and interpretation['incident_type_confidence'] < threshold:
        return True
    
    if 'casualties_confidence' in interpretation and interpretation['casualties_confidence'] < threshold:
        return True
    
    return False

# 2. Address Validation and Normalization
class AddressValidator:
    def __init__(self, addresses_file=None):
        """
        Initialize the address validator.
        
        Args:
            addresses_file (str, optional): Path to Delaware addresses CSV
        """
        self.addresses = {}
        self.streets = set()
        
        if addresses_file and os.path.exists(addresses_file):
            self._load_addresses(addresses_file)
        elif os.path.exists(DELAWARE_ADDRESSES_PATH):
            self._load_addresses(DELAWARE_ADDRESSES_PATH)
        else:
            print("Warning: No address database found. Using default validation.")
            self._load_default_addresses()
    
    def _load_addresses(self, filepath):
        """Load addresses from CSV file"""
        try:
            addresses_df = pd.read_csv(filepath)
            
            # Assuming the CSV has columns: address, street, city, zip
            for _, row in addresses_df.iterrows():
                full_address = row['address'].lower()
                street = row.get('street', '').lower()
                
                self.addresses[full_address] = {
                    'street': street,
                    'city': row.get('city', 'delaware').lower(),
                    'zip': row.get('zip', '')
                }
                
                if street:
                    self.streets.add(street)
            
            print(f"Loaded {len(self.addresses)} addresses and {len(self.streets)} streets")
        except Exception as e:
            print(f"Error loading addresses: {e}")
            self._load_default_addresses()
    
    def _load_default_addresses(self):
        """Load some default Delaware streets if no file is available"""
        default_streets = [
            "main street", "oak avenue", "elm road", "pine avenue", 
            "maple drive", "forest lane", "washington boulevard", 
            "liberty lane", "pinecrest drive", "troy road"
        ]
        
        for street in default_streets:
            self.streets.add(street)
    
    def validate_address(self, address):
        """
        Validate and normalize an address against the Delaware database.
        
        Args:
            address (str): Raw address string from transcript
            
        Returns:
            dict: Validation results with normalized address and flags
        """
        if not address:
            return {
                'normalized_address': 'unknown address',
                'valid': False,
                'confidence': 0.0,
                'needs_verification': True
            }
        
        address_lower = address.lower().strip()
        
        # Check for exact match
        if address_lower in self.addresses:
            return {
                'normalized_address': address_lower,
                'valid': True,
                'confidence': 1.0,
                'needs_verification': False
            }
        
        # Extract street name
        street_match = None
        match_confidence = 0.0
        
        for street in self.streets:
            if street in address_lower:
                # If we find a street, compute a simple confidence score
                # based on the length of the match relative to the address
                confidence = len(street) / len(address_lower)
                
                if confidence > match_confidence:
                    street_match = street
                    match_confidence = confidence
        
        if street_match:
            # Try to extract house number
            house_number = re.search(r'\b(\d+)\b', address_lower)
            house_num = house_number.group(1) if house_number else ""
            
            normalized = f"{house_num} {street_match}".strip()
            
            return {
                'normalized_address': normalized,
                'valid': True,
                'confidence': match_confidence,
                'needs_verification': match_confidence < 0.7
            }
        
        # No match found
        return {
            'normalized_address': address_lower,
            'valid': False,
            'confidence': 0.0,
            'needs_verification': True
        }

# 3. Priority Prediction System
class PriorityPredictor:
    def __init__(self, model_type="rule"):
        """
        Initialize priority predictor.
        
        Args:
            model_type (str): "rule" for rule-based or "ml" for ML-based
        """
        self.model_type = model_type
        self.ml_model = None
        self.incident_weights = {
            "structure fire": 4.0,
            "kitchen fire": 3.0,
            "electrical fire": 3.5,
            "gas leak": 4.0,
            "vehicle fire": 3.0,
            "wildfire": 4.5,
            "medical emergency": 3.0,
            "hazmat incident": 4.0
        }
        
        self.casualties_weights = {
            "children trapped": 2.0,
            "elderly person trapped": 1.8,
            "caller trapped": 1.5,
            "multiple people trapped": 2.0,
            "pets inside": 1.0,
            "caller escaped alone": 0.5,
            "everyone evacuated": 0.0,
            "none": 0.0
        }
        
        # Priority levels mapping (1-5 scale)
        self.priority_levels = {
            (0, 1.5): "LOW",
            (1.5, 2.5): "MEDIUM",
            (2.5, 3.5): "HIGH",
            (3.5, 4.5): "URGENT",
            (4.5, 5.0): "CRITICAL"
        }
        
        if model_type == "ml":
            self._initialize_ml_model()
    
    def _initialize_ml_model(self):
        """Initialize and train the ML regression model if training data is available"""
        try:
            # Try to load historical priority data
            if os.path.exists("data/historical_priorities.csv"):
                priorities_df = pd.read_csv("data/historical_priorities.csv")
                
                # Create features from incident_type and casualties
                X = pd.get_dummies(priorities_df[['incident_type', 'casualties']])
                y = priorities_df['priority']
                
                # Train a simple linear regression model
                self.ml_model = LinearRegression()
                self.ml_model.fit(X, y)
                
                # Evaluate model
                y_pred = self.ml_model.predict(X)
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                
                print(f"Priority prediction model trained. MSE: {mse:.4f}, R²: {r2:.4f}")
            else:
                print("No historical priority data found. Falling back to rule-based.")
                self.model_type = "rule"
        except Exception as e:
            print(f"Error training priority model: {e}")
            self.model_type = "rule"
    
    def predict_priority(self, incident_type, casualties):
        """
        Predict incident priority based on incident type and casualties.
        
        Args:
            incident_type (str): Type of incident
            casualties (str or dict): Casualties information
            
        Returns:
            dict: Priority information with numeric value and level
        """
        # For ML-based prediction
        if self.model_type == "ml" and self.ml_model:
            try:
                # Create feature vector
                features = pd.DataFrame({
                    'incident_type': [incident_type],
                    'casualties': [casualties if isinstance(casualties, str) else json.dumps(casualties)]
                })
                features = pd.get_dummies(features)
                
                # Predict
                priority = float(self.ml_model.predict(features)[0])
                
                # Ensure in range 1-5
                priority = max(1.0, min(5.0, priority))
            except Exception as e:
                print(f"ML prediction failed: {e}. Falling back to rule-based.")
                return self._rule_based_priority(incident_type, casualties)
        else:
            # Rule-based priority prediction
            return self._rule_based_priority(incident_type, casualties)
        
        # Map numeric priority to level
        level = self._priority_to_level(priority)
        
        return {
            'priority': round(priority, 1),
            'priority_level': level
        }
    
    def _rule_based_priority(self, incident_type, casualties):
        """Rule-based priority calculation"""
        # Get base priority from incident type
        base_priority = self.incident_weights.get(incident_type.lower(), 2.5)
        
        # Add casualties modifier
        if isinstance(casualties, dict):
            # For structured casualties
            modifier = 0
            if casualties.get('children', False):
                modifier += 2.0
            if casualties.get('elderly', False):
                modifier += 1.8
            if casualties.get('caller', False):
                modifier += 1.5
            if casualties.get('pets', False):
                modifier += 1.0
            
            # Normalize modifier for structured format
            modifier = min(modifier, 2.0)
        else:
            # For string casualties
            modifier = self.casualties_weights.get(casualties.lower(), 0.0)
        
        # Calculate final priority (scale 1-5)
        priority = min(5.0, base_priority + modifier / 2.0)
        
        # Map to priority level
        level = self._priority_to_level(priority)
        
        return {
            'priority': round(priority, 1),
            'priority_level': level
        }
    
    def _priority_to_level(self, priority):
        """Map numeric priority to text level"""
        for range_tuple, level in self.priority_levels.items():
            lower, upper = range_tuple
            if lower <= priority < upper:
                return level
        
        # Default fallback
        return "MEDIUM"

# 4. Structured Casualties Format
class CasualtyStructurer:
    def __init__(self):
        """Initialize the casualty structurer with category patterns"""
        self.categories = {
            'children': [
                r'child(ren)?', r'kids?', r'young', r'baby', r'babies', 
                r'infant', r'toddler', r'minor'
            ],
            'elderly': [
                r'elder(ly)?', r'old', r'senior', r'grandparent', 
                r'grandmother', r'grandfather'
            ],
            'pets': [
                r'pet', r'dog', r'cat', r'animal', r'bird', r'hamster',
                r'fish', r'rabbit'
            ],
            'caller': [
                r'caller', r'me', r'myself', r'I am', r"I'm", r'im trapped'
            ]
        }
        
        # Compile regex patterns
        self.compiled_patterns = {}
        for category, patterns in self.categories.items():
            self.compiled_patterns[category] = re.compile(
                r'(' + '|'.join(patterns) + r')', re.IGNORECASE
            )
    
    def structure_casualties(self, casualties_text):
        """
        Convert free-text casualties to structured format.
        
        Args:
            casualties_text (str): Free-text casualties description
            
        Returns:
            dict: Structured casualties with boolean flags
        """
        if not casualties_text or casualties_text.lower() in ['none', 'no casualties']:
            return {
                'children': False,
                'elderly': False,
                'pets': False,
                'caller': False,
                'text': casualties_text
            }
        
        # Initialize structure
        structured = {
            'children': False,
            'elderly': False,
            'pets': False,
            'caller': False,
            'text': casualties_text
        }
        
        # Check each category
        for category, pattern in self.compiled_patterns.items():
            if pattern.search(casualties_text):
                structured[category] = True
        
        # Special case for "trapped" without specific category
        if "trapped" in casualties_text.lower() and not any([
            structured['children'], structured['elderly'], 
            structured['pets'], structured['caller']
        ]):
            # Generic trapped person, assume caller
            structured['caller'] = True
        
        return structured

# Evaluation metrics for the enhanced features
def evaluate_confidence_scores(true_labels, predicted_labels, confidences):
    """
    Evaluate the quality of confidence scores.
    
    Args:
        true_labels (list): Ground truth labels
        predicted_labels (list): Predicted labels
        confidences (list): Confidence scores for predictions
        
    Returns:
        dict: Evaluation metrics
    """
    results = {
        'correct_predictions': 0,
        'high_confidence_correct': 0,
        'high_confidence_incorrect': 0,
        'low_confidence_correct': 0,
        'low_confidence_incorrect': 0,
        'average_confidence_correct': 0,
        'average_confidence_incorrect': 0
    }
    
    correct_confidences = []
    incorrect_confidences = []
    
    for true, pred, conf in zip(true_labels, predicted_labels, confidences):
        is_correct = true == pred
        
        if is_correct:
            results['correct_predictions'] += 1
            correct_confidences.append(conf)
            
            if conf >= 0.7:
                results['high_confidence_correct'] += 1
            else:
                results['low_confidence_correct'] += 1
        else:
            incorrect_confidences.append(conf)
            
            if conf >= 0.7:
                results['high_confidence_incorrect'] += 1
            else:
                results['low_confidence_incorrect'] += 1
    
    # Calculate averages
    results['average_confidence_correct'] = sum(correct_confidences) / len(correct_confidences) if correct_confidences else 0
    results['average_confidence_incorrect'] = sum(incorrect_confidences) / len(incorrect_confidences) if incorrect_confidences else 0
    
    # Calculate calibration metrics
    results['accuracy'] = results['correct_predictions'] / len(true_labels) if true_labels else 0
    
    # ECE (Expected Calibration Error) - simplified version
    conf_bins = defaultdict(lambda: {'correct': 0, 'total': 0})
    for true, pred, conf in zip(true_labels, predicted_labels, confidences):
        bin_idx = int(conf * 10) # 10 bins from 0.0-1.0
        conf_bins[bin_idx]['total'] += 1
        if true == pred:
            conf_bins[bin_idx]['correct'] += 1
    
    # Calculate ECE
    ece = 0
    total_samples = len(true_labels)
    
    for bin_idx, counts in conf_bins.items():
        if counts['total'] > 0:
            bin_conf = (bin_idx + 0.5) / 10  # Mid-point of bin
            bin_acc = counts['correct'] / counts['total']
            bin_weight = counts['total'] / total_samples
            ece += bin_weight * abs(bin_acc - bin_conf)
    
    results['ece'] = ece
    
    return results

def evaluate_address_validation(raw_addresses, validated_results):
    """
    Evaluate address validation performance.
    
    Args:
        raw_addresses (list): Raw addresses
        validated_results (list): Validation results dicts
        
    Returns:
        dict: Evaluation metrics
    """
    metrics = {
        'total': len(raw_addresses),
        'valid': 0,
        'invalid': 0,
        'needs_verification': 0,
        'avg_confidence': 0
    }
    
    confidences = []
    
    for result in validated_results:
        if result.get('valid', False):
            metrics['valid'] += 1
        else:
            metrics['invalid'] += 1
        
        if result.get('needs_verification', True):
            metrics['needs_verification'] += 1
        
        confidences.append(result.get('confidence', 0))
    
    metrics['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0
    metrics['verification_rate'] = metrics['needs_verification'] / metrics['total'] if metrics['total'] > 0 else 0
    
    return metrics

def evaluate_priority_prediction(true_priorities, predicted_priorities):
    """
    Evaluate priority prediction performance.
    
    Args:
        true_priorities (list): Ground truth priority values
        predicted_priorities (list): Predicted priority values
        
    Returns:
        dict: Evaluation metrics
    """
    metrics = {
        'mse': mean_squared_error(true_priorities, predicted_priorities),
        'r2': r2_score(true_priorities, predicted_priorities),
        'exact_match': 0,
        'within_0.5': 0,
        'within_1.0': 0
    }
    
    for true, pred in zip(true_priorities, predicted_priorities):
        if abs(true - pred) < 0.01:
            metrics['exact_match'] += 1
        
        if abs(true - pred) <= 0.5:
            metrics['within_0.5'] += 1
        
        if abs(true - pred) <= 1.0:
            metrics['within_1.0'] += 1
    
    total = len(true_priorities)
    metrics['exact_match_rate'] = metrics['exact_match'] / total if total > 0 else 0
    metrics['within_0.5_rate'] = metrics['within_0.5'] / total if total > 0 else 0
    metrics['within_1.0_rate'] = metrics['within_1.0'] / total if total > 0 else 0
    
    return metrics

def evaluate_casualties_structuring(text_casualties, structured_results):
    """
    Evaluate casualties structuring performance.
    
    Args:
        text_casualties (list): Original text casualty descriptions
        structured_results (list): Structured casualties dicts
        
    Returns:
        dict: Evaluation metrics
    """
    metrics = {
        'total': len(text_casualties),
        'children_identified': 0,
        'elderly_identified': 0,
        'pets_identified': 0,
        'caller_identified': 0,
        'total_categories_identified': 0
    }
    
    for structured in structured_results:
        if structured.get('children', False):
            metrics['children_identified'] += 1
        
        if structured.get('elderly', False):
            metrics['elderly_identified'] += 1
        
        if structured.get('pets', False):
            metrics['pets_identified'] += 1
        
        if structured.get('caller', False):
            metrics['caller_identified'] += 1
        
        # Count categories identified in this sample
        categories_count = sum([
            1 for cat in ['children', 'elderly', 'pets', 'caller'] 
            if structured.get(cat, False)
        ])
        
        metrics['total_categories_identified'] += categories_count
    
    metrics['avg_categories_per_casualty'] = (
        metrics['total_categories_identified'] / metrics['total'] 
        if metrics['total'] > 0 else 0
    )
    
    return metrics 
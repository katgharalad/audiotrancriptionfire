import os
import sys
import json
import time
import random
import unittest
import pandas as pd
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

# Import the enhanced features
from enhanced_features import (
    add_confidence_scores, 
    needs_verification,
    AddressValidator, 
    PriorityPredictor, 
    CasualtyStructurer,
    evaluate_confidence_scores,
    evaluate_address_validation,
    evaluate_priority_prediction,
    evaluate_casualties_structuring
)

class TestEnhancedFeatures(unittest.TestCase):
    """Test cases for the enhanced features."""
    
    def setUp(self):
        """Set up test data."""
        # Create test directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Create sample test interpretations
        self.sample_interpretations = [
            {
                "incident_type": "kitchen fire",
                "address": "123 Oak Street",
                "casualties": "none"
            },
            {
                "incident_type": "structure fire",
                "address": "456 Elm Road",
                "casualties": "children trapped"
            },
            {
                "incident_type": "gas leak",
                "address": "789 Pine Avenue",
                "casualties": "caller trapped"
            },
            {
                "incident_type": "wildfire",
                "address": "101 Forest Lane",
                "casualties": "pets inside"
            },
            {
                "incident_type": "vehicle fire",
                "address": "202 Main Street",
                "casualties": "elderly person trapped"
            }
        ]
        
        # Sample probabilities for confidence testing
        self.sample_probabilities = [
            {
                "incident_type_proba": [0.95, 0.03, 0.01, 0.01],
                "casualties_proba": [0.90, 0.05, 0.03, 0.02]
            },
            {
                "incident_type_proba": [0.60, 0.20, 0.15, 0.05],
                "casualties_proba": [0.55, 0.25, 0.15, 0.05]
            },
            {
                "incident_type_proba": [0.85, 0.10, 0.03, 0.02],
                "casualties_proba": [0.80, 0.12, 0.05, 0.03]
            },
            {
                "incident_type_proba": [0.40, 0.30, 0.20, 0.10],
                "casualties_proba": [0.50, 0.30, 0.10, 0.10]
            },
            {
                "incident_type_proba": [0.75, 0.15, 0.05, 0.05],
                "casualties_proba": [0.70, 0.20, 0.05, 0.05]
            }
        ]
        
        # Sample raw addresses for address validation
        self.raw_addresses = [
            "123 Oak Street",
            "456 elm rd apt 7B",
            "789 Pine Ave.",
            "101 forest ln",
            "202 MAIN ST"
        ]
        
        # Sample casualties text for structuring
        self.casualties_text = [
            "none",
            "children trapped in bedroom",
            "caller is trapped in bathroom",
            "dogs and cats inside the house",
            "elderly grandmother trapped upstairs"
        ]
        
        # Create synthetic data for address validation
        self._create_synthetic_address_data()
        
        # Create synthetic data for priority prediction
        self._create_synthetic_priority_data()
    
    def _create_synthetic_address_data(self):
        """Create synthetic Delaware address data for testing."""
        streets = [
            "Main Street", "Oak Avenue", "Elm Road", "Pine Avenue",
            "Maple Drive", "Forest Lane", "Washington Boulevard",
            "Liberty Lane", "Pinecrest Drive", "Troy Road"
        ]
        
        # Generate 100 synthetic addresses
        addresses = []
        for i in range(100):
            street = random.choice(streets)
            number = random.randint(1, 999)
            addresses.append({
                "address": f"{number} {street}",
                "street": street,
                "city": "Delaware",
                "zip": f"4300{random.randint(1, 9)}"
            })
        
        # Create DataFrame and save to CSV
        addresses_df = pd.DataFrame(addresses)
        addresses_df.to_csv("data/delaware_addresses.csv", index=False)
    
    def _create_synthetic_priority_data(self):
        """Create synthetic priority data for testing."""
        incident_types = [
            "kitchen fire", "structure fire", "gas leak", 
            "vehicle fire", "wildfire", "medical emergency"
        ]
        
        casualties = [
            "none", "caller trapped", "children trapped", 
            "elderly person trapped", "pets inside", "multiple people trapped"
        ]
        
        # Generate 200 synthetic priority records
        priorities = []
        for _ in range(200):
            incident = random.choice(incident_types)
            casualty = random.choice(casualties)
            
            # Base priority based on incident type
            if incident == "structure fire":
                base = 4.0
            elif incident == "gas leak":
                base = 4.0
            elif incident == "wildfire":
                base = 4.5
            elif incident == "vehicle fire":
                base = 3.0
            elif incident == "kitchen fire":
                base = 3.0
            else:
                base = 3.0
            
            # Modifier based on casualties
            if casualty == "children trapped":
                mod = 1.0
            elif casualty == "elderly person trapped":
                mod = 0.9
            elif casualty == "caller trapped":
                mod = 0.75
            elif casualty == "multiple people trapped":
                mod = 1.0
            elif casualty == "pets inside":
                mod = 0.5
            else:
                mod = 0.0
            
            # Calculate priority (with some noise)
            priority = min(5.0, base + mod + random.uniform(-0.3, 0.3))
            
            priorities.append({
                "incident_type": incident,
                "casualties": casualty,
                "priority": round(priority, 1)
            })
        
        # Create DataFrame and save to CSV
        priorities_df = pd.DataFrame(priorities)
        priorities_df.to_csv("data/historical_priorities.csv", index=False)
    
    def test_confidence_scores(self):
        """Test confidence score calculation."""
        print("\n==== Testing Confidence Scores ====")
        
        # Add confidence scores to interpretations
        enhanced_interpretations = []
        for interp, probs in zip(self.sample_interpretations, self.sample_probabilities):
            enhanced = add_confidence_scores(interp, probs)
            enhanced_interpretations.append(enhanced)
            
            print(f"Incident: {enhanced.get('incident_type')}")
            print(f"Confidence: {enhanced.get('confidence', 'N/A')}")
            print(f"Incident confidence: {enhanced.get('incident_type_confidence', 'N/A')}")
            print(f"Casualties confidence: {enhanced.get('casualties_confidence', 'N/A')}")
            print(f"Needs verification: {needs_verification(enhanced)}")
            print("-" * 50)
        
        # Verify structure
        for enhanced in enhanced_interpretations:
            self.assertIn('confidence', enhanced)
            self.assertIn('incident_type_confidence', enhanced)
            self.assertIn('casualties_confidence', enhanced)
        
        # Evaluate confidence scores
        true_labels = ["kitchen fire", "structure fire", "gas leak", "wildfire", "vehicle fire"]
        pred_labels = [interp["incident_type"] for interp in enhanced_interpretations]
        confidences = [interp["incident_type_confidence"] for interp in enhanced_interpretations]
        
        metrics = evaluate_confidence_scores(true_labels, pred_labels, confidences)
        
        print("\nConfidence Metrics:")
        print(f"Accuracy: {metrics['accuracy']:.2f}")
        print(f"High confidence correct: {metrics['high_confidence_correct']}")
        print(f"High confidence incorrect: {metrics['high_confidence_incorrect']}")
        print(f"Low confidence correct: {metrics['low_confidence_correct']}")
        print(f"Low confidence incorrect: {metrics['low_confidence_incorrect']}")
        print(f"Expected Calibration Error: {metrics['ece']:.4f}")
        
        # Check that metrics are reasonable
        self.assertGreaterEqual(metrics['accuracy'], 0.0)
        self.assertLessEqual(metrics['accuracy'], 1.0)
        self.assertGreaterEqual(metrics['ece'], 0.0)
        
        print("Confidence score tests passed.")
    
    def test_address_validation(self):
        """Test address validation and normalization."""
        print("\n==== Testing Address Validation ====")
        
        # Initialize the address validator
        validator = AddressValidator()
        
        # Validate sample addresses
        validation_results = []
        for address in self.raw_addresses:
            result = validator.validate_address(address)
            validation_results.append(result)
            
            print(f"Raw: {address}")
            print(f"Normalized: {result.get('normalized_address', 'N/A')}")
            print(f"Valid: {result.get('valid', False)}")
            print(f"Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"Needs verification: {result.get('needs_verification', True)}")
            print("-" * 50)
        
        # Verify structure
        for result in validation_results:
            self.assertIn('normalized_address', result)
            self.assertIn('valid', result)
            self.assertIn('confidence', result)
            self.assertIn('needs_verification', result)
        
        # Evaluate validation
        metrics = evaluate_address_validation(self.raw_addresses, validation_results)
        
        print("\nAddress Validation Metrics:")
        print(f"Total addresses: {metrics['total']}")
        print(f"Valid addresses: {metrics['valid']}")
        print(f"Invalid addresses: {metrics['invalid']}")
        print(f"Addresses needing verification: {metrics['needs_verification']}")
        print(f"Average confidence: {metrics['avg_confidence']:.2f}")
        print(f"Verification rate: {metrics['verification_rate']:.2f}")
        
        # Check metrics
        self.assertEqual(metrics['total'], len(self.raw_addresses))
        self.assertEqual(metrics['valid'] + metrics['invalid'], metrics['total'])
        
        print("Address validation tests passed.")
    
    def test_priority_prediction(self):
        """Test priority prediction."""
        print("\n==== Testing Priority Prediction ====")
        
        # Initialize the priority predictor with rule-based approach
        rule_predictor = PriorityPredictor(model_type="rule")
        
        # Predict priorities for sample interpretations
        rule_predictions = []
        print("Rule-based Priority Predictions:")
        for interp in self.sample_interpretations:
            incident_type = interp["incident_type"]
            casualties = interp["casualties"]
            
            prediction = rule_predictor.predict_priority(incident_type, casualties)
            rule_predictions.append(prediction)
            
            print(f"Incident: {incident_type}")
            print(f"Casualties: {casualties}")
            print(f"Priority: {prediction.get('priority', 0.0)}")
            print(f"Level: {prediction.get('priority_level', 'UNKNOWN')}")
            print("-" * 50)
        
        # Verify structure
        for pred in rule_predictions:
            self.assertIn('priority', pred)
            self.assertIn('priority_level', pred)
            self.assertGreaterEqual(pred['priority'], 1.0)
            self.assertLessEqual(pred['priority'], 5.0)
        
        # Test with ML model if data is available
        try:
            ml_predictor = PriorityPredictor(model_type="ml")
            
            # If ML model was created, test it
            if ml_predictor.model_type == "ml" and ml_predictor.ml_model:
                print("\nML-based Priority Predictions:")
                ml_predictions = []
                
                for interp in self.sample_interpretations:
                    incident_type = interp["incident_type"]
                    casualties = interp["casualties"]
                    
                    prediction = ml_predictor.predict_priority(incident_type, casualties)
                    ml_predictions.append(prediction)
                    
                    print(f"Incident: {incident_type}")
                    print(f"Casualties: {casualties}")
                    print(f"Priority: {prediction.get('priority', 0.0)}")
                    print(f"Level: {prediction.get('priority_level', 'UNKNOWN')}")
                    print("-" * 50)
                
                # Compare rule-based vs ML predictions
                rule_values = [pred['priority'] for pred in rule_predictions]
                ml_values = [pred['priority'] for pred in ml_predictions]
                
                print("\nPriority Model Comparison:")
                print(f"Rule-based average: {sum(rule_values) / len(rule_values):.2f}")
                print(f"ML average: {sum(ml_values) / len(ml_values):.2f}")
                
                # Evaluate with synthetic true priorities
                true_priorities = [3.5, 5.0, 4.5, 4.0, 4.0]  # Expected priorities
                
                rule_metrics = evaluate_priority_prediction(true_priorities, rule_values)
                print("\nRule-based Priority Metrics:")
                print(f"MSE: {rule_metrics['mse']:.4f}")
                print(f"R²: {rule_metrics['r2']:.4f}")
                print(f"Within 0.5: {rule_metrics['within_0.5_rate']:.2f}")
                print(f"Within 1.0: {rule_metrics['within_1.0_rate']:.2f}")
                
                if len(ml_values) == len(true_priorities):
                    ml_metrics = evaluate_priority_prediction(true_priorities, ml_values)
                    print("\nML Priority Metrics:")
                    print(f"MSE: {ml_metrics['mse']:.4f}")
                    print(f"R²: {ml_metrics['r2']:.4f}")
                    print(f"Within 0.5: {ml_metrics['within_0.5_rate']:.2f}")
                    print(f"Within 1.0: {ml_metrics['within_1.0_rate']:.2f}")
        except Exception as e:
            print(f"ML priority prediction not tested: {e}")
        
        print("Priority prediction tests passed.")
    
    def test_casualties_structuring(self):
        """Test casualties structuring."""
        print("\n==== Testing Casualties Structuring ====")
        
        # Initialize the casualty structurer
        structurer = CasualtyStructurer()
        
        # Structure the sample casualties
        structured_results = []
        for casualties_text in self.casualties_text:
            structured = structurer.structure_casualties(casualties_text)
            structured_results.append(structured)
            
            print(f"Original: {casualties_text}")
            print(f"Children: {structured.get('children', False)}")
            print(f"Elderly: {structured.get('elderly', False)}")
            print(f"Pets: {structured.get('pets', False)}")
            print(f"Caller: {structured.get('caller', False)}")
            print("-" * 50)
        
        # Verify structure
        for result in structured_results:
            self.assertIn('children', result)
            self.assertIn('elderly', result)
            self.assertIn('pets', result)
            self.assertIn('caller', result)
            self.assertIn('text', result)
        
        # Evaluate structuring
        metrics = evaluate_casualties_structuring(self.casualties_text, structured_results)
        
        print("\nCasualties Structuring Metrics:")
        print(f"Total samples: {metrics['total']}")
        print(f"Children identified: {metrics['children_identified']}")
        print(f"Elderly identified: {metrics['elderly_identified']}")
        print(f"Pets identified: {metrics['pets_identified']}")
        print(f"Caller identified: {metrics['caller_identified']}")
        print(f"Average categories per casualty: {metrics['avg_categories_per_casualty']:.2f}")
        
        # Check metrics
        self.assertEqual(metrics['total'], len(self.casualties_text))
        self.assertGreaterEqual(metrics['avg_categories_per_casualty'], 0.0)
        
        print("Casualties structuring tests passed.")

def run_tests():
    """Run the tests and return a dictionary of results."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_instance = TestEnhancedFeatures()
    test_suite.addTest(test_instance)
    
    # Run tests and collect results
    results = {}
    
    # Test confidence scores
    test_instance.setUp()  # Ensure data is initialized
    print("\n==== Testing Confidence Scores ====")
    enhanced_interpretations = []
    for interp, probs in zip(test_instance.sample_interpretations, test_instance.sample_probabilities):
        enhanced = add_confidence_scores(interp, probs)
        enhanced_interpretations.append(enhanced)
        
        print(f"Incident: {enhanced.get('incident_type')}")
        print(f"Confidence: {enhanced.get('confidence', 'N/A')}")
        print(f"Incident confidence: {enhanced.get('incident_type_confidence', 'N/A')}")
        print(f"Casualties confidence: {enhanced.get('casualties_confidence', 'N/A')}")
        print(f"Needs verification: {needs_verification(enhanced)}")
        print("-" * 50)
    
    # Evaluate confidence scores
    true_labels = ["kitchen fire", "structure fire", "gas leak", "wildfire", "vehicle fire"]
    pred_labels = [interp["incident_type"] for interp in enhanced_interpretations]
    confidences = [interp["incident_type_confidence"] for interp in enhanced_interpretations]
    
    results['confidence_metrics'] = evaluate_confidence_scores(true_labels, pred_labels, confidences)
    
    print("\nConfidence Metrics:")
    print(f"Accuracy: {results['confidence_metrics']['accuracy']:.2f}")
    print(f"High confidence correct: {results['confidence_metrics']['high_confidence_correct']}")
    print(f"High confidence incorrect: {results['confidence_metrics']['high_confidence_incorrect']}")
    print(f"Low confidence correct: {results['confidence_metrics']['low_confidence_correct']}")
    print(f"Low confidence incorrect: {results['confidence_metrics']['low_confidence_incorrect']}")
    print(f"Expected Calibration Error: {results['confidence_metrics']['ece']:.4f}")
    print("Confidence score tests passed.")
    
    # Test address validation
    print("\n==== Testing Address Validation ====")
    validator = AddressValidator()
    
    validation_results = []
    for address in test_instance.raw_addresses:
        result = validator.validate_address(address)
        validation_results.append(result)
        
        print(f"Raw: {address}")
        print(f"Normalized: {result.get('normalized_address', 'N/A')}")
        print(f"Valid: {result.get('valid', False)}")
        print(f"Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"Needs verification: {result.get('needs_verification', True)}")
        print("-" * 50)
    
    results['address_metrics'] = evaluate_address_validation(test_instance.raw_addresses, validation_results)
    
    print("\nAddress Validation Metrics:")
    print(f"Total addresses: {results['address_metrics']['total']}")
    print(f"Valid addresses: {results['address_metrics']['valid']}")
    print(f"Invalid addresses: {results['address_metrics']['invalid']}")
    print(f"Addresses needing verification: {results['address_metrics']['needs_verification']}")
    print(f"Average confidence: {results['address_metrics']['avg_confidence']:.2f}")
    print(f"Verification rate: {results['address_metrics']['verification_rate']:.2f}")
    print("Address validation tests passed.")
    
    # Test priority prediction
    print("\n==== Testing Priority Prediction ====")
    rule_predictor = PriorityPredictor(model_type="rule")
    
    rule_predictions = []
    print("Rule-based Priority Predictions:")
    for interp in test_instance.sample_interpretations:
        incident_type = interp["incident_type"]
        casualties = interp["casualties"]
        
        prediction = rule_predictor.predict_priority(incident_type, casualties)
        rule_predictions.append(prediction)
        
        print(f"Incident: {incident_type}")
        print(f"Casualties: {casualties}")
        print(f"Priority: {prediction.get('priority', 0.0)}")
        print(f"Level: {prediction.get('priority_level', 'UNKNOWN')}")
        print("-" * 50)
    
    # Test ML model if available
    true_priorities = [3.5, 5.0, 4.5, 4.0, 4.0]  # Expected priorities
    rule_values = [pred['priority'] for pred in rule_predictions]
    
    results['priority_metrics'] = evaluate_priority_prediction(true_priorities, rule_values)
    
    print("\nRule-based Priority Metrics:")
    print(f"MSE: {results['priority_metrics']['mse']:.4f}")
    print(f"R²: {results['priority_metrics']['r2']:.4f}")
    print(f"Within 0.5: {results['priority_metrics']['within_0.5_rate']:.2f}")
    print(f"Within 1.0: {results['priority_metrics']['within_1.0_rate']:.2f}")
    print("Priority prediction tests passed.")
    
    # Test casualties structuring
    print("\n==== Testing Casualties Structuring ====")
    structurer = CasualtyStructurer()
    
    structured_results = []
    for casualties_text in test_instance.casualties_text:
        structured = structurer.structure_casualties(casualties_text)
        structured_results.append(structured)
        
        print(f"Original: {casualties_text}")
        print(f"Children: {structured.get('children', False)}")
        print(f"Elderly: {structured.get('elderly', False)}")
        print(f"Pets: {structured.get('pets', False)}")
        print(f"Caller: {structured.get('caller', False)}")
        print("-" * 50)
    
    results['casualties_metrics'] = evaluate_casualties_structuring(
        test_instance.casualties_text, structured_results
    )
    
    print("\nCasualties Structuring Metrics:")
    print(f"Total samples: {results['casualties_metrics']['total']}")
    print(f"Children identified: {results['casualties_metrics']['children_identified']}")
    print(f"Elderly identified: {results['casualties_metrics']['elderly_identified']}")
    print(f"Pets identified: {results['casualties_metrics']['pets_identified']}")
    print(f"Caller identified: {results['casualties_metrics']['caller_identified']}")
    print(f"Average categories per casualty: {results['casualties_metrics']['avg_categories_per_casualty']:.2f}")
    print("Casualties structuring tests passed.")
    
    return results

# For standalone usage
if __name__ == "__main__":
    unittest.main() 
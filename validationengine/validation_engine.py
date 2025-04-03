import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import re
import json
import time
from pathlib import Path

class AddressValidationEngine:
    def __init__(self, data_dir='.'):
        """Initialize the validation engine with Delaware County datasets."""
        self.data_dir = Path(data_dir)
        self.datasets = {}
        self._load_datasets()
        
    def _load_datasets(self):
        """Load all required datasets from CSV files."""
        # Define dataset file paths 
        dataset_files = {
            'address_points': 'Address_Point_6449015960905250632 (1).csv',
            'street_centerlines': 'Street_Centerline_7861883908334951619.csv',
            'msag': 'MSAG_155522220392559522.csv',
            'parcels': 'Parcel_188782905266197535.csv',
            'zip_codes': 'Zip_Code_-4600858990630826378.csv'
        }
        
        # Load each dataset
        print("Loading datasets...")
        for key, filename in dataset_files.items():
            file_path = self.data_dir / filename
            try:
                # For large files, we load only essential columns initially
                if key in ['address_points', 'parcels', 'street_centerlines']:
                    self.datasets[key] = pd.read_csv(file_path, low_memory=False)
                else:
                    self.datasets[key] = pd.read_csv(file_path)
                print(f"Loaded {key} dataset: {len(self.datasets[key])} records")
            except Exception as e:
                print(f"Error loading {key} dataset: {e}")
    
    def parse_transcript_for_location(self, text):
        """
        Extract location information from transcript text.
        
        Args:
            text (str): Raw transcript text
            
        Returns:
            dict: Dictionary containing extracted address or landmark information
        """
        # Simple pattern matching for addresses
        address_pattern = r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Highway|Hwy|Way|Court|Ct|Circle|Cir|Place|Pl|Terrace|Ter)\b'
        address_matches = re.findall(address_pattern, text, re.IGNORECASE)
        
        # Look for potential landmarks (capitalized phrases)
        landmark_pattern = r'\b([A-Z][a-z]*(?:\s+[A-Z][a-z]*)+)(?:\s+(?:School|Church|Hospital|Library|Park|Mall|Center|Store|Building|Station)s?)?\b'
        landmark_matches = re.findall(landmark_pattern, text)
        
        result = {
            'raw_text': text,
            'extracted_addresses': address_matches,
            'potential_landmarks': landmark_matches,
            'has_address': len(address_matches) > 0,
            'has_landmark': len(landmark_matches) > 0
        }
        
        return result
    
    def validate_against_address_points(self, parsed_data):
        """
        Validate extracted address against Delaware County address points.
        
        Args:
            parsed_data (dict): Output from parse_transcript_for_location
            
        Returns:
            dict: Validation results with confidence scores
        """
        results = {
            'valid_addresses': [],
            'confidence_scores': [],
            'best_match': None,
            'best_confidence': 0.0
        }
        
        if not parsed_data['has_address']:
            return results
        
        # Get address columns from our dataset
        if 'FULLADDR' in self.datasets['address_points'].columns:
            address_col = 'FULLADDR'
        elif 'ADDRESS' in self.datasets['address_points'].columns:
            address_col = 'ADDRESS'
        else:
            # Find a suitable address column
            for col in self.datasets['address_points'].columns:
                if 'ADDR' in col.upper() or 'ADDRESS' in col.upper():
                    address_col = col
                    break
        
        # Sample some addresses for validation (for efficiency)
        sample_addresses = self.datasets['address_points'][address_col].dropna().sample(min(1000, len(self.datasets['address_points']))).tolist()
        
        for extracted_addr in parsed_data['extracted_addresses']:
            # Perform fuzzy matching
            matches = process.extractBests(
                extracted_addr, 
                sample_addresses, 
                scorer=fuzz.token_set_ratio, 
                score_cutoff=60,
                limit=3
            )
            
            if matches:
                for match, score in matches:
                    normalized_score = score / 100.0
                    results['valid_addresses'].append(match)
                    results['confidence_scores'].append(normalized_score)
                    
                    if normalized_score > results['best_confidence']:
                        results['best_match'] = match
                        results['best_confidence'] = normalized_score
        
        return results
    
    def landmark_to_address(self, landmark_name):
        """
        Convert a landmark name to its corresponding address.
        
        Args:
            landmark_name (str): Name of landmark to search for
            
        Returns:
            dict: Information about the landmark and its address
        """
        result = {
            'landmark': landmark_name,
            'found': False,
            'address': None,
            'confidence': 0.0,
            'lat': None,
            'lon': None
        }
        
        # First check parcel data which often contains landmark names
        potential_columns = []
        
        for col in self.datasets['parcels'].columns:
            if 'NAME' in col.upper() or 'OWNER' in col.upper() or 'DESC' in col.upper():
                potential_columns.append(col)
        
        if potential_columns:
            for col in potential_columns:
                # Sample for efficiency
                sample_landmarks = self.datasets['parcels'][col].dropna().sample(min(2000, len(self.datasets['parcels']))).tolist()
                
                matches = process.extractBests(
                    landmark_name,
                    sample_landmarks,
                    scorer=fuzz.token_set_ratio,
                    score_cutoff=70,
                    limit=3
                )
                
                if matches:
                    best_match, score = matches[0]
                    result['found'] = True
                    result['confidence'] = score / 100.0
                    
                    # Find corresponding address in the dataset
                    matching_rows = self.datasets['parcels'][self.datasets['parcels'][col] == best_match]
                    
                    if not matching_rows.empty:
                        # Get the address information
                        for addr_col in self.datasets['parcels'].columns:
                            if 'ADDR' in addr_col.upper() or 'ADDRESS' in addr_col.upper():
                                result['address'] = matching_rows[addr_col].iloc[0]
                                break
                        
                        # Get coordinates if available
                        for lat_col in self.datasets['parcels'].columns:
                            if 'LAT' in lat_col.upper() or 'Y' == lat_col.upper():
                                result['lat'] = matching_rows[lat_col].iloc[0]
                            if 'LON' in lat_col.upper() or 'X' == lat_col.upper():
                                result['lon'] = matching_rows[lat_col].iloc[0]
                        
                        break
        
        # If not found in parcels, try address points
        if not result['found']:
            # Similar search in address points dataset
            for col in self.datasets['address_points'].columns:
                if 'NAME' in col.upper() or 'LABEL' in col.upper() or 'DESC' in col.upper():
                    # Similar process as above for address points
                    pass
        
        return result
    
    def assign_zip_jurisdiction(self, address_or_coords):
        """
        Assign zip code and jurisdiction information based on address or coordinates.
        
        Args:
            address_or_coords: Either a string address or a (lat, lon) tuple
            
        Returns:
            dict: Zip code and jurisdiction information
        """
        result = {
            'zip_code': None,
            'township': None,
            'municipality': None,
            'confidence': 0.0
        }
        
        # If we have an address, try to find it in address points
        if isinstance(address_or_coords, str):
            address = address_or_coords
            
            # Search in address points dataset
            potential_matches = []
            for col in self.datasets['address_points'].columns:
                if 'ADDR' in col.upper() or 'ADDRESS' in col.upper():
                    filtered = self.datasets['address_points'][self.datasets['address_points'][col].str.contains(address, case=False, na=False)]
                    if not filtered.empty:
                        potential_matches.append(filtered)
            
            # If we found matches, extract zip and jurisdiction
            if potential_matches:
                match_df = pd.concat(potential_matches).drop_duplicates()
                
                # Extract zip code
                for col in match_df.columns:
                    if 'ZIP' in col.upper() or 'POSTAL' in col.upper():
                        result['zip_code'] = match_df[col].iloc[0]
                        break
                
                # Try to get jurisdiction info
                lat, lon = None, None
                for col in match_df.columns:
                    if 'LAT' in col.upper() or 'Y' == col.upper():
                        lat = match_df[col].iloc[0]
                    if 'LON' in col.upper() or 'X' == col.upper():
                        lon = match_df[col].iloc[0]
                
                if lat and lon:
                    # Use point-in-polygon with MSAG data
                    # For simplicity, we'll use the first matching jurisdiction in MSAG
                    # A proper implementation would use spatial operations with geopandas
                    result['confidence'] = 0.7
            
            # If not found, try using zip code dataset matches
            if not result['zip_code']:
                for zip_data in self.datasets['zip_codes'].itertuples():
                    if hasattr(zip_data, 'Name') and zip_data.Name in address:
                        result['zip_code'] = getattr(zip_data, 'Zip Code', None)
                        result['confidence'] = 0.5
                        break
        
        # Basic implementation - would need spatial libraries for proper point-in-polygon check
        # with the actual boundaries
        
        return result
    
    def generate_validation_report(self, transcript):
        """
        Full pipeline to validate addresses in transcript.
        
        Args:
            transcript (str): Raw transcript text
            
        Returns:
            dict: Complete validation report
        """
        start_time = time.time()
        
        # Parse the transcript
        parsed_data = self.parse_transcript_for_location(transcript)
        
        result = {
            'raw_transcript': transcript,
            'address_validity': False,
            'confidence_score': 0.0,
            'matched_address': None,
            'matched_landmark': None,
            'needs_verification': True,
            'zip_code': None,
            'jurisdiction': None,
            'processing_time_ms': 0
        }
        
        # If we found addresses, validate them
        if parsed_data['has_address']:
            address_validation = self.validate_against_address_points(parsed_data)
            
            if address_validation['best_match']:
                result['address_validity'] = True
                result['confidence_score'] = address_validation['best_confidence']
                result['matched_address'] = address_validation['best_match']
                
                # Get zip and jurisdiction
                zip_info = self.assign_zip_jurisdiction(address_validation['best_match'])
                result['zip_code'] = zip_info['zip_code']
                result['jurisdiction'] = zip_info['township'] or zip_info['municipality']
                
                # Determine if manual verification is needed
                result['needs_verification'] = address_validation['best_confidence'] < 0.8
        
        # If we found landmarks, try to resolve them
        elif parsed_data['has_landmark'] and parsed_data['potential_landmarks']:
            best_landmark = None
            best_confidence = 0.0
            
            for landmark in parsed_data['potential_landmarks']:
                landmark_info = self.landmark_to_address(landmark)
                
                if landmark_info['found'] and landmark_info['confidence'] > best_confidence:
                    best_landmark = landmark_info
                    best_confidence = landmark_info['confidence']
            
            if best_landmark:
                result['matched_landmark'] = best_landmark['landmark']
                result['matched_address'] = best_landmark['address']
                result['confidence_score'] = best_landmark['confidence']
                result['address_validity'] = True
                
                # Get zip and jurisdiction
                if best_landmark['address']:
                    zip_info = self.assign_zip_jurisdiction(best_landmark['address'])
                    result['zip_code'] = zip_info['zip_code']
                    result['jurisdiction'] = zip_info['township'] or zip_info['municipality']
                
                # Landmarks usually need verification
                result['needs_verification'] = result['confidence_score'] < 0.9
        
        end_time = time.time()
        result['processing_time_ms'] = round((end_time - start_time) * 1000, 2)
        
        return result

# Example usage
if __name__ == "__main__":
    # Initialize the validation engine
    engine = AddressValidationEngine()
    
    # Test with sample data
    test_transcript = "There's a fire in front of Smith Elementary and kids are stuck inside."
    result = engine.generate_validation_report(test_transcript)
    
    # Print the result
    print(json.dumps(result, indent=2)) 
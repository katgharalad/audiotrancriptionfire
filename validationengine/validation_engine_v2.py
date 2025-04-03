import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import re
import json
import time
import os
from pathlib import Path

class AddressValidationEngine:
    def __init__(self, data_dir=None):
        """Initialize the validation engine with Delaware County datasets."""
        # If data_dir is not provided, use the directory where this script is located
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.data_dir = Path(data_dir)
        print(f"Initializing validation engine with data directory: {self.data_dir}")
        
        self.datasets = {}
        self._load_datasets()
        
        # Create a landmark dictionary for common Delaware landmarks
        self.landmark_dict = {
            "muirwood village": {"address": "162 MUIRWOOD VILLAGE DR", 
                               "zip": "43015", 
                               "confidence": 0.95,
                               "jurisdiction": "Delaware"},
            "muirwood village apts": {"address": "162 MUIRWOOD VILLAGE DR", 
                                    "zip": "43015", 
                                    "confidence": 0.95,
                                    "jurisdiction": "Delaware"},
            "delaware city police": {"address": "70 N UNION ST", 
                                   "zip": "43015", 
                                   "confidence": 0.9,
                                   "jurisdiction": "Delaware"},
            "delaware police department": {"address": "70 N UNION ST", 
                                         "zip": "43015", 
                                         "confidence": 0.9,
                                         "jurisdiction": "Delaware"},
            "stratford ecological center": {"address": "3083 LIBERTY RD", 
                                          "zip": "43015", 
                                          "confidence": 0.88,
                                          "jurisdiction": "Delaware"},
            "kroger": {"address": "801 N HOUK RD", 
                     "zip": "43015", 
                     "confidence": 0.85,
                     "jurisdiction": "Delaware"},
            "liberty township fire station": {"address": "7761 LIBERTY RD", 
                                            "zip": "43015", 
                                            "confidence": 0.9,
                                            "jurisdiction": "Liberty Township"},
            "camp lazarus": {"address": "4422 COLUMBUS PIKE", 
                           "zip": "43015", 
                           "confidence": 0.92,
                           "jurisdiction": "Delaware"},
            "glenross golf clubhouse": {"address": "231 CLUBHOUSE DR", 
                                      "zip": "43015", 
                                      "confidence": 0.9,
                                      "jurisdiction": "Delaware"},
            "hayes high school": {"address": "289 EUCLID AVE", 
                                "zip": "43015", 
                                "confidence": 0.92,
                                "jurisdiction": "Delaware"},
            "rutherford b hayes high school": {"address": "289 EUCLID AVE", 
                                             "zip": "43015", 
                                             "confidence": 0.92,
                                             "jurisdiction": "Delaware"},
            "delaware county ems": {"address": "10 COURT ST", 
                                  "zip": "43015", 
                                  "confidence": 0.9,
                                  "jurisdiction": "Delaware"}
        }
        
        # Define relative location terms and their impact on confidence
        self.relative_location_terms = {
            "across from": {"confidence_modifier": 0.9, "is_exact": False},
            "across the street from": {"confidence_modifier": 0.9, "is_exact": False},
            "behind": {"confidence_modifier": 0.85, "is_exact": False},
            "next to": {"confidence_modifier": 0.95, "is_exact": False},
            "near": {"confidence_modifier": 0.8, "is_exact": False},
            "close to": {"confidence_modifier": 0.8, "is_exact": False},
            "in front of": {"confidence_modifier": 0.9, "is_exact": False},
            "by": {"confidence_modifier": 0.8, "is_exact": False},
            "at": {"confidence_modifier": 1.0, "is_exact": True},
            "outside": {"confidence_modifier": 0.9, "is_exact": False},
            "inside": {"confidence_modifier": 1.0, "is_exact": True}
        }
        
    def _load_datasets(self):
        """Load all required datasets from CSV files."""
        # Define dataset file patterns and fallbacks
        dataset_files = {
            'address_points': ['Address_Point_*.csv', 'Address_Point_6449015960905250632 (1).csv'],
            'street_centerlines': ['Street_Centerline_*.csv', 'Street_Centerline_7861883908334951619.csv'],
            'msag': ['MSAG_*.csv', 'MSAG_155522220392559522.csv'],
            'parcels': ['Parcel_*.csv', 'Parcel_188782905266197535.csv'],
            'zip_codes': ['Zip_Code_*.csv', 'Zip_Code_-4600858990630826378.csv']
        }
        
        print("Loading datasets...")
        print(f"Looking in directory: {self.data_dir}")
        
        # Create fallback data if needed
        self._create_fallback_data()
        
        # For each dataset, try to load it
        for key, file_patterns in dataset_files.items():
            found_file = None
            
            # Try each pattern in order
            for pattern in file_patterns:
                # Handle exact filename and glob patterns
                if '*' in pattern:
                    matching_files = list(self.data_dir.glob(pattern))
                    if matching_files:
                        found_file = str(matching_files[0])
                        break
                else:
                    specific_file = self.data_dir / pattern
                    if specific_file.exists():
                        found_file = str(specific_file)
                        break
            
            if found_file:
                try:
                    print(f"Loading {key} from {found_file}")
                    self.datasets[key] = pd.read_csv(found_file, low_memory=False)
                    print(f"  ✓ Loaded {key} dataset: {len(self.datasets[key])} records")
                except Exception as e:
                    print(f"  ✗ Error loading {key} dataset: {e}")
                    print(f"    Using fallback data for {key}")
                    self.datasets[key] = self._get_fallback_data(key)
            else:
                print(f"  ! No file found for {key} dataset. Using fallback data.")
                self.datasets[key] = self._get_fallback_data(key)
    
    def _create_fallback_data(self):
        """Create minimal fallback data for testing when real data is not available."""
        self.fallback_data = {
            'address_points': pd.DataFrame({
                'FULLADDR': ['123 MAIN ST', '456 OAK AVE', '789 PINE RD', '321 LIBERTY ST', 
                           '100 SANDUSKY ST', '200 WINTER ST', '300 CENTRAL AVE'],
                'ZIP': ['43015', '43015', '43015', '43015', '43015', '43015', '43015'],
                'MUNI': ['Delaware', 'Delaware', 'Delaware', 'Delaware', 'Delaware', 'Delaware', 'Delaware']
            }),
            'street_centerlines': pd.DataFrame({
                'FULLNAME': ['MAIN ST', 'OAK AVE', 'PINE RD', 'LIBERTY ST', 
                           'SANDUSKY ST', 'WINTER ST', 'CENTRAL AVE'],
                'ZIPL': ['43015', '43015', '43015', '43015', '43015', '43015', '43015'],
                'MUNI': ['Delaware', 'Delaware', 'Delaware', 'Delaware', 'Delaware', 'Delaware', 'Delaware']
            }),
            'msag': pd.DataFrame({
                'ESN': ['101', '102', '103', '104'],
                'COMMUNITY': ['Delaware', 'Liberty Township', 'Orange Township', 'Powell']
            }),
            'parcels': pd.DataFrame({
                'PARCELID': ['1', '2', '3', '4', '5'],
                'OWNER': ['Smith Elementary School', 'Delaware City Police', 'Kroger', 
                        'Liberty Township Fire', 'Hayes High School'],
                'SITEADDRESS': ['450 N LIBERTY ST', '70 N UNION ST', '801 N HOUK RD', 
                             '7761 LIBERTY RD', '289 EUCLID AVE']
            }),
            'zip_codes': pd.DataFrame({
                'ZIP': ['43015', '43065', '43021', '43074'],
                'PO_NAME': ['Delaware', 'Powell', 'Galena', 'Sunbury']
            })
        }
    
    def _get_fallback_data(self, key):
        """Get fallback data for a specific dataset."""
        if key in self.fallback_data:
            print(f"  → Using fallback data for {key} ({len(self.fallback_data[key])} records)")
            return self.fallback_data[key]
        else:
            # Return an empty DataFrame with basic columns
            return pd.DataFrame(columns=['ID', 'NAME', 'ADDRESS'])
    
    def parse_transcript_for_location(self, text):
        """
        Extract location information from transcript text.
        
        Args:
            text (str): Raw transcript text
            
        Returns:
            dict: Dictionary containing extracted address or landmark information
        """
        # Better pattern matching for addresses, including those with directional prefixes
        address_pattern = r'\b\d+\s+(?:[NSEW]\s+)?[A-Za-z\s\-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Highway|Hwy|Way|Court|Ct|Circle|Cir|Place|Pl|Terrace|Ter|Village|DR)\b'
        address_matches = re.findall(address_pattern, text, re.IGNORECASE)
        
        # Also look for simpler address patterns (like house number + street name without type)
        simple_address_pattern = r'\b\d+\s+(?:[NSEW]\s+)?[A-Za-z]+(?:\s+[A-Za-z]+){1,2}\b'
        simple_matches = re.findall(simple_address_pattern, text, re.IGNORECASE)
        
        # Combine and deduplicate
        all_addresses = []
        for addr in address_matches + simple_matches:
            normalized = re.sub(r'\s+', ' ', addr.strip())
            if normalized not in all_addresses:
                all_addresses.append(normalized)
        
        # Look for potential landmarks (capitalized phrases)
        landmark_pattern = r'\b([A-Z][a-z]*(?:\s+[A-Z][a-z]*)+)(?:\s+(?:School|Church|Hospital|Library|Park|Mall|Center|Store|Building|Station|Department|Apts|Apartments|Village|Post)s?)?\b'
        landmark_matches = re.findall(landmark_pattern, text)
        
        # Find relative location terms
        relative_terms = []
        for term in self.relative_location_terms.keys():
            if term.lower() in text.lower():
                relative_terms.append(term)
                
        result = {
            'raw_text': text,
            'extracted_addresses': all_addresses,
            'potential_landmarks': landmark_matches,
            'relative_terms': relative_terms,
            'has_address': len(all_addresses) > 0,
            'has_landmark': len(landmark_matches) > 0,
            'has_relative_terms': len(relative_terms) > 0
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
            'best_confidence': 0.0,
            'full_address': None  # Store the complete address
        }
        
        if not parsed_data['has_address']:
            return results
        
        # Get address columns from our dataset
        address_col = None
        house_num_col = None
        street_name_col = None
        street_prefix_col = None
        street_type_col = None
        full_street_name_col = None
        
        # First, try to find the best columns for address components
        for col in self.datasets['address_points'].columns:
            col_upper = col.upper()
            if 'FULLADDR' in col_upper or 'FULL_ADDRESS' in col_upper:
                address_col = col
            elif 'HOUSE' in col_upper or 'ADDR_NUM' in col_upper or 'NUMBER' in col_upper:
                house_num_col = col
            elif 'STREET_NAME' in col_upper:
                street_name_col = col
            elif 'PREFIX' in col_upper:
                street_prefix_col = col
            elif 'TYPE' in col_upper and 'STREET' in col_upper:
                street_type_col = col
            elif 'FULL_STREET' in col_upper or 'FULLSTREET' in col_upper:
                full_street_name_col = col
        
        # If no full address column found, use individual components or fallback
        if not address_col:
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
        if address_col:
            sample_addresses = self.datasets['address_points'][address_col].dropna().sample(min(1000, len(self.datasets['address_points']))).tolist()
        else:
            # Create addresses from components if available
            sample_addresses = []
            sample_df = self.datasets['address_points'].sample(min(1000, len(self.datasets['address_points'])))
            
            for _, row in sample_df.iterrows():
                address_parts = []
                
                # Get house number
                if house_num_col and pd.notna(row.get(house_num_col)):
                    address_parts.append(str(row[house_num_col]))
                
                # Get street prefix (like N, S, E, W)
                if street_prefix_col and pd.notna(row.get(street_prefix_col)):
                    address_parts.append(str(row[street_prefix_col]))
                
                # Get street name
                if street_name_col and pd.notna(row.get(street_name_col)):
                    address_parts.append(str(row[street_name_col]))
                elif full_street_name_col and pd.notna(row.get(full_street_name_col)):
                    address_parts.append(str(row[full_street_name_col]))
                
                # Get street type (like ST, RD, AVE)
                if street_type_col and pd.notna(row.get(street_type_col)):
                    address_parts.append(str(row[street_type_col]))
                
                if address_parts:
                    sample_addresses.append(" ".join(address_parts))
        
        for extracted_addr in parsed_data['extracted_addresses']:
            # Store the original extracted address for full address preservation
            original_addr = extracted_addr
            
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
                    
                    # Check if the match is just a number (house number only)
                    if match.isdigit():
                        # Try to find the full address for this house number
                        if house_num_col:
                            matching_rows = self.datasets['address_points'][
                                self.datasets['address_points'][house_num_col].astype(str) == match
                            ].head(1)
                            
                            if not matching_rows.empty:
                                # Construct full address
                                full_addr_parts = []
                                row = matching_rows.iloc[0]
                                
                                # Add house number
                                full_addr_parts.append(match)
                                
                                # Add prefix if available
                                if street_prefix_col and pd.notna(row.get(street_prefix_col)):
                                    full_addr_parts.append(str(row[street_prefix_col]))
                                
                                # Add street name
                                if street_name_col and pd.notna(row.get(street_name_col)):
                                    full_addr_parts.append(str(row[street_name_col]))
                                elif full_street_name_col and pd.notna(row.get(full_street_name_col)):
                                    full_addr_parts.append(str(row[full_street_name_col]))
                                
                                # Add street type
                                if street_type_col and pd.notna(row.get(street_type_col)):
                                    full_addr_parts.append(str(row[street_type_col]))
                                
                                if len(full_addr_parts) > 1:  # Only use if we have more than just the number
                                    match = " ".join(full_addr_parts)
                                    print(f"Enhanced match: {match}")
                    
                    results['valid_addresses'].append(match)
                    results['confidence_scores'].append(normalized_score)
                    
                    if normalized_score > results['best_confidence']:
                        results['best_match'] = match
                        results['best_confidence'] = normalized_score
                        results['full_address'] = original_addr  # Preserve the full extracted address
        
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
            'lon': None,
            'zip': None,
            'jurisdiction': None
        }
        
        # First check predefined landmark dictionary
        best_match = None
        best_score = 0
        
        for key, value in self.landmark_dict.items():
            score = fuzz.token_sort_ratio(landmark_name.lower(), key.lower())
            if score > 70 and score > best_score:
                best_match = key
                best_score = score
        
        if best_match:
            result['found'] = True
            result['address'] = self.landmark_dict[best_match]["address"]
            result['confidence'] = self.landmark_dict[best_match]["confidence"] * (best_score / 100.0)
            result['zip'] = self.landmark_dict[best_match]["zip"]
            result['jurisdiction'] = self.landmark_dict[best_match]["jurisdiction"]
            return result
            
        # If not in predefined list, check parcel data which often contains landmark names
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
            
            # Extract any zip code from the address
            zip_pattern = r'\b\d{5}\b'
            zip_matches = re.findall(zip_pattern, address)
            if zip_matches:
                result['zip_code'] = zip_matches[0]
                result['confidence'] = 0.9
            
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
        
        # If we still don't have a zip code, default to Delaware
        if not result['zip_code']:
            result['zip_code'] = "43015"  # Default Delaware OH zip
            result['confidence'] = 0.5
        else:
            # Ensure proper 5-digit ZIP code format
            try:
                # Convert to integer and format as 5-digit string
                zip_int = int(result['zip_code'])
                result['zip_code'] = f"{zip_int:05d}"
            except:
                # If it's not a valid integer, use default
                result['zip_code'] = "43015"
        
        return result
    
    def adjust_confidence_for_relative_terms(self, parsed_data, base_confidence):
        """
        Adjust confidence score based on relative location terms.
        
        Args:
            parsed_data (dict): Output from parse_transcript_for_location
            base_confidence (float): Base confidence score to adjust
            
        Returns:
            float: Adjusted confidence score
        """
        # Default no adjustment
        adjusted_confidence = base_confidence
        
        if parsed_data['has_relative_terms']:
            # Find the relative term with the highest impact
            highest_modifier = 1.0
            for term in parsed_data['relative_terms']:
                if term.lower() in self.relative_location_terms:
                    modifier = self.relative_location_terms[term.lower()]['confidence_modifier']
                    if modifier < highest_modifier:
                        highest_modifier = modifier
            
            # Apply the modifier
            adjusted_confidence = base_confidence * highest_modifier
        
        return adjusted_confidence
    
    def generate_validation_report(self, transcript):
        """
        Generate a complete validation report with confidence scores and verification flags.
        
        Args:
            transcript (str): Raw transcript text
            
        Returns:
            dict: Complete validation report with matched address, confidence, etc.
        """
        try:
            # Start timing
            start_time = time.time()
            
            # Parse the transcript for location information
            parsed_data = self.parse_transcript_for_location(transcript)
            
            # Initialize result structure
            result = {
                'address_validity': False,
                'matched_address': "Unknown address",
                'matched_landmark': None,
                'confidence_score': 0.0,
                'zip_code': None,
                'jurisdiction': None,
                'needs_verification': True,
                'processing_time_ms': 0
            }
            
            try:
                # Try to validate against address points
                address_validation = self.validate_against_address_points(parsed_data)
                
                # If we have a valid address
                if address_validation.get('best_match') and address_validation.get('best_confidence', 0) > 0.6:
                    result['address_validity'] = True
                    
                    # Check if best_match contains street information or is just a number
                    best_match = address_validation.get('best_match', "")
                    if best_match and not best_match.isdigit():
                        result['matched_address'] = best_match
                    else:
                        # Try to combine with extracted street name from transcript
                        for addr in parsed_data.get('extracted_addresses', []):
                            # If the address contains both a number and street information
                            if best_match in addr and len(addr) > len(best_match):
                                result['matched_address'] = addr
                                break
                        else:
                            # Fallback to just the matched number if we can't enhance it
                            result['matched_address'] = best_match
                    
                    result['confidence_score'] = address_validation['best_confidence']
                    
                    # Assign zip code and jurisdiction
                    zip_jurisdiction = self.assign_zip_jurisdiction(result['matched_address'])
                    result['zip_code'] = zip_jurisdiction.get('zip_code')
                    result['jurisdiction'] = zip_jurisdiction.get('municipality') or zip_jurisdiction.get('township')
                    
                    # Determine if verification is needed based on confidence
                    result['needs_verification'] = result['confidence_score'] < 0.75
            
            except Exception as e:
                print(f"Error during address validation: {e}")
                import traceback
                traceback.print_exc()
                # Continue processing with other methods
            
            # If we don't have a valid address or confidence is low, try landmark matching
            if not result['address_validity'] or result['confidence_score'] < 0.7:
                for landmark_name in parsed_data.get('potential_landmarks', []):
                    try:
                        landmark_result = self.landmark_to_address(landmark_name)
                        
                        if landmark_result['found'] and landmark_result['confidence'] > result['confidence_score']:
                            result['matched_landmark'] = landmark_name
                            result['matched_address'] = landmark_result['address']
                            result['confidence_score'] = landmark_result['confidence']
                            result['zip_code'] = landmark_result.get('zip')
                            result['jurisdiction'] = landmark_result.get('jurisdiction')
                            result['address_validity'] = True
                            result['needs_verification'] = result['confidence_score'] < 0.75
                    except Exception as e:
                        print(f"Error during landmark validation: {e}")
                        # Continue with next landmark
            
            # Check for relative location terms and adjust confidence
            if parsed_data.get('has_relative_terms', False):
                for term in parsed_data.get('relative_terms', []):
                    if term in self.relative_location_terms:
                        # Adjust confidence based on relative term
                        result['confidence_score'] *= self.relative_location_terms[term]['confidence_modifier']
                        # If not exact location, may need verification
                        if not self.relative_location_terms[term]['is_exact']:
                            result['needs_verification'] = True
            
            # Record processing time
            end_time = time.time()
            result['processing_time_ms'] = round((end_time - start_time) * 1000)
            
            return result
            
        except Exception as e:
            # Return a minimal result in case of error
            print(f"Error generating validation report: {e}")
            return {
                'address_validity': False,
                'matched_address': "Error processing address",
                'matched_landmark': None,
                'confidence_score': 0.0,
                'zip_code': None,
                'jurisdiction': None,
                'needs_verification': True,
                'processing_time_ms': 0,
                'error': str(e)
            }

# Example usage
if __name__ == "__main__":
    # Initialize the validation engine
    engine = AddressValidationEngine()
    
    # Test with sample data
    test_transcript = "There's a fire in front of Smith Elementary and kids are stuck inside."
    result = engine.generate_validation_report(test_transcript)
    
    # Print the result
    print(json.dumps(result, indent=2)) 
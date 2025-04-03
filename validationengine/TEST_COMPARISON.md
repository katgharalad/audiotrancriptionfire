# Test Results vs. Expected Results

This document compares our current validation engine test results with the expected/desired results for each test case.

## Test Cases Comparison

| # | Test Case | Current Result | Expected Result | Gap Analysis |
|---|-----------|----------------|-----------------|--------------|
| 1 | "There is a fire at 162 MUIRWOOD VILLAGE DR." | ✅ Address: 162<br>Confidence: 1.0<br>Zip: 6087 | ✅ Address: 162 MUIRWOOD VILLAGE DR<br>Confidence: ~0.95+<br>Zip: 43015 | Partial match (only number)<br>Incorrect zip code format |
| 2 | "I'm outside Muirwood Village Apts and it's burning." | ❌ No match<br>Confidence: 0.0 | ✅ Address: 162 MUIRWOOD VILLAGE DR<br>Landmark: Muirwood Village Apts<br>Confidence: ~0.90+ | Landmark not in database<br>Landmark dictionary needed |
| 3 | "Smoke coming from the building near Muirwood Village Apts on MUIRWOOD VILLAGE DR." | ❌ No match<br>Confidence: 0.0 | ✅ Address: 162 MUIRWOOD VILLAGE DR<br>Landmark: Muirwood Village Apts<br>Confidence: ~0.88+ | Landmark not in database<br>Proximity terms not handled |
| 4 | "I'm across the street from Muirwood Village Apts, something exploded." | ❌ No match<br>Confidence: 0.0 | ✅ Address: 160–164 MUIRWOOD VILLAGE DR<br>Landmark: Muirwood Village Apts<br>Confidence: ~0.85 | Relative location ("across from") not handled<br>Landmark not in database |
| 5 | "I'm at the Muirwood Village Apts in DELAWARE, help!" | ❌ No match<br>Confidence: 0.0 | ✅ Address: 162 MUIRWOOD VILLAGE DR<br>Landmark: Muirwood Village Apts<br>Confidence: ~0.92 | Landmark not in database<br>Location context not leveraged |
| 6 | "Massive fire behind Muirwood Village Apts on MUIRWOOD VILLAGE DR." | ❌ No match<br>Confidence: 0.0 | ✅ Address: 162 MUIRWOOD VILLAGE DR<br>Landmark: Muirwood Village Apts<br>Confidence: ~0.85–0.9 | Relative location ("behind") not handled<br>Landmark not in database |
| 7 | "There's something burning at 1000 Sunbury Rd." | ✅ Address: 1000<br>Confidence: 1.0<br>Zip: 9600 | ✅ Address: 1000 Sunbury Rd<br>Confidence: ~0.95<br>Zip: 43015 | Partial match (only number)<br>Incorrect zip code format |
| 8 | "Outside the Delaware City Police Department — send help." | ✅ Address: 1 S SANDUSKY ST<br>Confidence: 0.9<br>Zip: 2315 | ✅ Address: 70 N UNION ST<br>Landmark: Delaware City Police Dept<br>Confidence: ~0.9+<br>Zip: 43015 | Incorrect address match<br>Incorrect zip code format |
| 9 | "Fire in the woods by the Stratford Ecological Center." | ❌ No match<br>Confidence: 0.0 | ✅ Address: 3083 LIBERTY RD<br>Landmark: Stratford Ecological Center<br>Confidence: ~0.88–0.9<br>Zip: 43015 | Landmark not in database<br>Proximity terms ("by") not handled |
| 10 | "Explosion near the Kroger parking lot on North Houk Rd." | ✅ Address: 4715 NORTH SHORE DR<br>Confidence: 0.72<br>Zip: 9410 | ✅ Address: 801 N HOUK RD<br>Landmark: Kroger<br>Confidence: ~0.85–0.9<br>Zip: 43015 | Incorrect address match<br>Incorrect zip code format |
| 11 | "Caller reports flames behind Liberty Township Fire Station." | ✅ Address: 3883 ST RT 605 S<br>Confidence: 1.0 | ✅ Address: 7761 LIBERTY RD<br>Landmark: Liberty Township Fire Station<br>Confidence: ~0.9+<br>Zip: 43015 | Address mismatch<br>Missing zip code |
| 12 | "Kids trapped at Camp Lazarus. Structure fire." | ❌ No match<br>Confidence: 0.0 | ✅ Address: 4422 COLUMBUS PIKE<br>Landmark: Camp Lazarus BSA<br>Confidence: ~0.92<br>Zip: 43015 | Landmark not in database |
| 13 | "Smoke at Glenross Golf Clubhouse." | ✅ Address: 3001 HACKBERRY RD<br>Confidence: 0.8 | ✅ Address: 231 CLUBHOUSE DR<br>Landmark: Glenross Golf Clubhouse<br>Confidence: ~0.9<br>Zip: 43015 | Address mismatch<br>Missing zip code |
| 14 | "Fire near Hayes High School football stadium!" | ❌ No match<br>Confidence: 0.0 | ✅ Address: 289 EUCLID AVE<br>Landmark: Rutherford B. Hayes High School<br>Confidence: ~0.92<br>Zip: 43015 | Landmark not in database<br>Proximity terms ("near") not handled |
| 15 | "Smoke coming from behind the Delaware County EMS Post." | ✅ Address: 7131 TEMPERANCE POINT ST<br>Confidence: 0.76<br>Zip: 8707 | ✅ Address: 10 COURT ST<br>Landmark: Delaware County EMS Post<br>Confidence: ~0.88–0.92<br>Zip: 43015 | Address mismatch<br>Incorrect zip code format<br>Relative location ("behind") not handled |

## Summary of Key Gaps

1. **Landmark Recognition**:
   - 8 of 15 test cases (53%) failed to recognize landmarks that should have been matched
   - Many key Delaware landmarks are missing from the database

2. **Address Format**:
   - 3 of 7 successful matches (43%) only returned the address number without the street name
   - Several addresses were incorrectly matched to wrong locations

3. **Zip Code Issues**:
   - None of the matches returned the expected 5-digit zip code format (43015)
   - All zip codes were either missing or in an incorrect format

4. **Relative Location Terms**:
   - Failed to handle relative location terms like "behind," "near," "by," and "across from"
   - These terms are common in emergency calls and critical for correct location identification

5. **Jurisdiction Assignment**:
   - No test cases correctly identified the jurisdiction (township or municipality)

## Implementation Priority

Based on this analysis, we recommend focusing on these improvements first:

1. Build a comprehensive landmark dictionary for Delaware County with correct addresses
2. Fix address normalization to return complete addresses
3. Standardize zip code format to 5-digit codes
4. Implement handling for relative location terms
5. Add jurisdiction lookup based on address or coordinates 
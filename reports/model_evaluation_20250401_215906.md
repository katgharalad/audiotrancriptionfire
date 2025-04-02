# Fire Incident ML Model Evaluation

*Report generated on 2025-04-01 21:59:06*

## Dataset Statistics

- Total samples: 31896
- Speaker 2 (caller) samples: 28195
- Test set size: 5639

## Incident Type Classification

- Accuracy: 1.0000
- F1 Score (weighted): 1.0000

**Classification Report:**

```
                 precision    recall  f1-score   support

electrical fire       1.00      1.00      1.00       705
    false alarm       1.00      1.00      1.00       733
       gas leak       1.00      1.00      1.00       702
industrial fire       1.00      1.00      1.00       686
   kitchen fire       1.00      1.00      1.00       721
 structure fire       1.00      1.00      1.00       699
   vehicle fire       1.00      1.00      1.00       700
       wildfire       1.00      1.00      1.00       693

       accuracy                           1.00      5639
      macro avg       1.00      1.00      1.00      5639
   weighted avg       1.00      1.00      1.00      5639
```

## Casualties Classification

- Accuracy: 1.0000
- F1 Score (weighted): 1.0000

**Classification Report:**

```
                        precision    recall  f1-score   support

  caller escaped alone       1.00      1.00      1.00       786
        caller trapped       1.00      1.00      1.00       872
      children trapped       1.00      1.00      1.00       836
elderly person trapped       1.00      1.00      1.00       766
                  none       1.00      1.00      1.00       784
           pets inside       1.00      1.00      1.00       787
unknown number trapped       1.00      1.00      1.00       808

              accuracy                           1.00      5639
             macro avg       1.00      1.00      1.00      5639
          weighted avg       1.00      1.00      1.00      5639
```

## Sample Predictions

### Example 2328

**Transcript:** there s a vehicle fire at 247 s liberty st apt 4 casualties reported caller escaped alone

**Incident Type:**
- True: vehicle fire
- Predicted: vehicle fire

**Casualties:**
- True: caller escaped alone
- Predicted: caller escaped alone

### Example 3472

**Transcript:** there s a electrical fire at 5127 harvest loop no one is hurt

**Incident Type:**
- True: electrical fire
- Predicted: electrical fire

**Casualties:**
- True: none
- Predicted: none

### Example 283

**Transcript:** there s a industrial fire at 232 stonhope dr casualties reported elderly person trapped

**Incident Type:**
- True: industrial fire
- Predicted: industrial fire

**Casualties:**
- True: elderly person trapped
- Predicted: elderly person trapped

### Example 1403

**Transcript:** there s a wildfire at 100 georgetowne dr apt 206 casualties reported children trapped

**Incident Type:**
- True: wildfire
- Predicted: wildfire

**Casualties:**
- True: children trapped
- Predicted: children trapped

### Example 2601

**Transcript:** there s a kitchen fire at 192 trotter s cir no one is hurt

**Incident Type:**
- True: kitchen fire
- Predicted: kitchen fire

**Casualties:**
- True: none
- Predicted: none

## Conclusion

The models show excellent performance on the test data. They are ready for deployment in a fire dispatch environment.


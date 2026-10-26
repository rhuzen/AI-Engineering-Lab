### Profile Report: Shipment Data

1. **Duplicate shipment rows**  
   **Evidence:** The raw data had 200 duplicate rows and 100,200 rows in total.  
   **Action:** The cleaning workflow removed the duplicates, leaving 100,000 rows.  
   **Reason:** This prevents the same shipment from being counted twice.

2. **Missing shipment weights**  
   **Evidence:** 301 values were missing in `weight_kg`.  
   **Action:** Missing values were filled with the median weight for the same commodity.  
   **Reason:** Weight varies by commodity, so using the commodity-specific median provides a more suitable estimate.

3. **Missing lane distance**  
   **Evidence:** 1 value was missing in `distance_km`.  
   **Action:** The missing value was filled with the median of the known lane distances.  
   **Reason:** The median provides an estimate based on the available lane-distance data.

4. **Very long delays**  
   **Evidence:** 80 shipments had delays over 100 hours. The 75th percentile was 1.97 hours, and the longest delay was 227.88 hours. All 80 delays matched the arrival timestamps within 0.01 hour.  
   **Decision:** These values were kept unchanged because they were within the allowed range of `-48` to `240` hours and matched the arrival timestamps.  
   **Reason:** Long delays are not necessarily data errors when the recorded timestamps support them.

5. **Status mismatch — custom cleaning rule**  
   **Evidence:** The raw data contained 99 shipments marked `In Transit` despite having a recorded `actual_arrival`. The portfolio pipeline identified and corrected these 99 rows.  
   **Action:** In `make_silver.py`, shipments marked `In Transit` with a non-null `actual_arrival` were changed to `Delivered`.  
   **Reason:** A recorded arrival indicates that the shipment has reached its destination. This is an additional cleaning rule introduced for the portfolio pipeline; it should not be attributed to the original notebook unless that notebook also implements the rule.

### Additional checks

- **Non-positive weights:** 0 rows found; no rows were removed.
- **Impossible transit times (`planned_arrival <= planned_departure`):** 0 rows found; no rows were removed.
[//]: # To create a virtual enviornment use:
[//]: # `$ python3 -m venv MY_VENV`

[//]: # To activate it use:
[//]: # `$ source MY_VENV/bin/activate`

[//]: # To deactive it use:
[//]: # `$ deactivate`

# UConn Rec Center Occupancy Analysis by Myself & [mineable3](https://github.com/mineable3)

## Overview

This project analyzes occupancy data collected from the UConn Rec Center over the Fall Semester (October - December 2025), correcting for time zone differences and daylight saving time (DST). The goal is to determine trends in gym usage by weekday, weekend, and hour of the day, enabling better understanding of peak hours and facility usage patterns.

## Methodology

### 0. Data Collection

- Hosted python script on a cloud server to periodically (every 15 minutes) grab the occupancy value from the UConn Rec website (https://app.safespace.io/api/display/live-occupancy/86fb9e11)
- Used Selenium to grab occupancy value and applied a timestap by using time library
- Wrote collected data to a CSV file

### 1. Data Cleaning and Parsing

- Read CSV data using pandas
- Remove error rows where data was missing or invalid
- Convert separate date and time columns into a single datetime object

### 2. Time Zone Correction (After Realizing the scraper script was synced to the server's local time)

The collected data timestamps are **3 hours and 45 minutes ahead** of Eastern Time.
- Subtract 3:45 from raw timestamps
- Localize to `America/New_York` timezone using pytz
- Handle DST transition (November 2, 2025)

### 3. Feature Extraction

- Extract weekday names and hours
- Create `within_hours` helper function to identify timestamps within operational hours:
  - **Weekdays (Mon-Fri):** 6 AM - 10 PM
  - **Weekends (Sat-Sun):** 10 AM - 5 PM
- Create `day_type` field (Weekday/Weekend) for comparative analysis

### 4. Aggregation

- Convert weekday column to Categorical type to preserve natural order (Mon → Sun)
- Group by weekday and hour to compute average occupancy

### 5. Visualization

- Use matplotlib to create three analytical graphs:
  1. **Bar chart:** Average occupancy by day of week
  2. **Line plot:** Average occupancy by hour
  3. **Comparative line plot:** Weekday vs weekend hourly patterns
- Format axes and gridlines for readability
- Maintain consistent ordering for clear interpretation
- Added console statistics (Total Data Points, Mean Occupancy, etc.)

## Key Findings

Based on the analysis, typical patterns observed include:

- As the week goes on, less people are at the UConn Rec Center on Average, with the most people at the Rec Center on Wednesday
- On average, the highest rates where people enter the Rec Center are from 6-8 AM, 10AM-12PM, and 3-5 PM, with this pattern mosty applying on the Weekdays and somewhat on the Weekends
- On average, the lowest rates where people enter the Rec Center are from 8-10 AM, 1-3 PM, and anytime after 6PM (for the Weekdays), indicating that these are the less crowded periods and the best times to go
- The busiest times at the Rec Center are at 1 PM and 5 PM on the Weekdays and 12 PM and 4 PM on the Weekends due to the peaks in occupancy at those times

## Important Notes

- **DST Handling:** The DST transition on November 2, 2025 is handled by assuming the times have been standardized to EST 
- **Time Zone Offset:** The 3hr and 45min offset appears to be constant across before and after DST change
- **Operational Hours:** Data outside operational hours is filtered out to focus on actual gym usage and prevent issues with mean calculation

## Limitations

- Rows with errors or missing times are dropped, but large gaps can introduce bias
- Fixed interval sampling may smooth out short-term peaks, underestimating maximum occupancy
- Students are only required to scan an ID on the way in, not out. This makes the true occupancy unknown because they don't know exactly how many people have left
- The occupancy on the website doesn't truly reflect how full the Rec center feels. For example, a fitness class may inflate the occupancy, but because classes are limited to studios it won't affect regular occupants.

## Future Notes

- Perhaps make a ML algorithm from this data
- Collect more data to compare patterns with the spring semester
- Introduct data collection at random intervals


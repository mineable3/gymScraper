# NOTES:
# - Put all function definitions at the top and all the code in a main method.
# - Rounding to the nearest hour loses data, why not do a scatter plot of occupancy over time?
# - What about daily averages over time, maybe there are dips during exam times?
# - Explain the mid-day (hours 12-15) slump in growth.
# - Hypothesize why the peaks in occupancy are where they are for weekday and weekends.
# - What about first and second derivatives, how quickly people fill up the rec?
# - Fix Limitations section, there are much more professional mistakes we can cite. For example, how much of our data is statistically significant? Could lost data actually affect our results (mathematically)?


import pandas as pd
import pytz
import matplotlib.pyplot as plt

# For displaying in ubuntu
# Needs python3-tk to be installed
import matplotlib
matplotlib.use('TkAgg')

df = pd.read_csv('cordGraph.csv')

# Collect raw datetime (ignore our weekday column :( )
# TODO: Add 2025 as the year in the argument so we don't need
# to go back and change it with a lambda function
df['datetime_raw'] = pd.to_datetime(
    df['Month'] + ' ' + df['day'].astype(str) + ' ' + df['time'],
    format='%b %d %H:%M:%S',
    errors='coerce'
)

# Set year to 2025 (needed for dst)
df['datetime_raw'] = df['datetime_raw'].apply(lambda dt: dt.replace(year=2025))

# Drop rows with invalid datetime
# TODO: df still says 4660 rows, but the [] notations has shrunk
df = df.dropna(subset=['datetime_raw'])

# Correct for timezone offset (data is 3hrs 45mins ahead)
df['datetime_est'] = df['datetime_raw'] - pd.Timedelta(hours=3, minutes=45)

# Apply DST correction (data is in EST)
# TODO: rename eastern for clarity
eastern = pytz.timezone('America/New_York')
# TODO: What is a 'dst'?
# TODO: What does this do? I thought we corrected for timezone above?
df['datetime_est_dst'] = df['datetime_est'].apply(
    # TODO: does the variable need to be called dt (date time)?
    lambda dt: eastern.localize(dt, is_dst=False)
)

# Extract weekday, hour, minute
df['weekday'] = df['datetime_est_dst'].dt.day_name().str[:3]
df['hour'] = df['datetime_est_dst'].dt.hour
df['minute'] = df['datetime_est_dst'].dt.minute

# Weekday/Weekend hours filter
def within_valid_hours(row):
    if row['weekday'] in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
        # Weekdays: 6 AM to 10 PM
        # TODO: This works? You don't need an and keyword?
        return 6 <= row['hour'] <= 22
    else:  # Sat, Sun
        # Weekends: 10 AM to 5 PM
        # TODO: This works? You don't need an and keyword?
        return 10 <= row['hour'] <= 17

# TODO: I'm guessing this filters out data that their axis 1 data (hour)
#   returns false for the within_valid_hours function
df['within_hours'] = df.apply(within_valid_hours, axis=1)

# TODO: How does this work? (filter out of hours entries)
df_valid = df[df['within_hours']].copy()

# Convert occupancy to numeric
# TODO: What does this do? Is this just a type cast?
df_valid['occupancy'] = pd.to_numeric(df_valid['occupancy'], errors='coerce')

## -------------------------------------------------------------
# Plotting

# by day of week
weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
# TODO: What does this do? This does nothing?
df_valid['weekday'] = pd.Categorical(df_valid['weekday'], categories=weekday_order, ordered=True)
# TODO: Explain how this works?
weekday_avg = df_valid.groupby('weekday', observed=False)['occupancy'].mean()
# TODO: This does nothing?
weekday_avg = weekday_avg.reindex(weekday_order)

plt.figure(figsize=(10, 6))
plt.bar(weekday_avg.index, weekday_avg.values, color='skyblue')
plt.xlabel('Day of the Week')
plt.ylabel('Average Occupancy')
plt.title('Average Occupancy by Day of the Week')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# time of day
hourly_avg = df_valid.groupby('hour')['occupancy'].mean()

plt.figure(figsize=(12, 6))
plt.plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2, markersize=6)
plt.xlabel('Hour of Day')
plt.ylabel('Average Occupancy')
plt.title('Average Occupancy by Hour of Day')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(range(0, 24))
plt.tight_layout()
plt.show()

# weekday vs weekend
df_valid['day_type'] = df_valid['weekday'].apply(
    lambda x: 'Weekday' if x in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] else 'Weekend'
)

hourly_by_type = df_valid.groupby(['day_type', 'hour'])['occupancy'].mean().unstack(level=0)

plt.figure(figsize=(12, 6))
if 'Weekday' in hourly_by_type.columns:
    plt.plot(hourly_by_type.index, hourly_by_type['Weekday'], 
             marker='o', linewidth=2, label='Weekday', markersize=6)
if 'Weekend' in hourly_by_type.columns:
    plt.plot(hourly_by_type.index, hourly_by_type['Weekend'], 
             marker='s', linewidth=2, label='Weekend', markersize=6)
plt.xlabel('Hour of Day')
plt.ylabel('Average Occupancy')
plt.title('Average Occupancy by Hour: Weekday vs Weekend')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(range(0, 24))
plt.tight_layout()
plt.show()

# summary stats
print("\n-- Gym Occupancy Summary --")
print(f"Total data points: {len(df)}")
print(f"Valid hours data points: {len(df_valid)}")
print(f"\nOverall Statistics:")
print(f"  Mean occupancy: {df_valid['occupancy'].mean():.1f}")
print(f"  Median occupancy: {df_valid['occupancy'].median():.1f}")
print(f"  Max occupancy: {df_valid['occupancy'].max():.0f}")
print(f"  Min occupancy: {df_valid['occupancy'].min():.0f}")

print(f"\nBy Day Type:")
print(df_valid.groupby('day_type')['occupancy'].agg(['mean', 'median', 'max']))

print(f"\nBusiest Hours (Top 5):")
print(hourly_avg.sort_values(ascending=False).head())

print(f"\nBusiest Days (Top 3):")
print(weekday_avg.sort_values(ascending=False).head(3))

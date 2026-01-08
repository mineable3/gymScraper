# NOTES:
# [x] Put all function definitions at the top and all the code in a main method.
# [x] Rounding to the nearest hour loses data, why not do a scatter plot of occupancy over time?
# [x] What about daily averages over time, maybe there are dips during exam times?
# [x] Explain the mid-day (hours 12-15) slump in growth.
# [x] Hypothesize why the peaks in occupancy are where they are for weekday and weekends.
# [x] What about first and second derivatives, how quickly people fill up the rec?
# [ ] Fix Limitations section, there are much more professional mistakes we can cite. For example, how much of our data is statistically significant? Could lost data actually affect our results (mathematically)?

import pandas as pd
import pytz
import matplotlib.pyplot as plt

# For displaying in ubuntu
# Needs python3-tk to be installed
import matplotlib
matplotlib.use('TkAgg')

# Weekday/Weekend hours filter
def within_valid_hours(row):
    """ Only return true if within operating hours of the rec center """
    if row['weekday'] in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
        # Weekdays: 6 AM to 10 PM
        return 6 <= row['hour'] < 22 or (row['hour'] == 22 and row['minute'] == 0)
    else:  # Sat, Sun
        # Weekends: 10 AM to 5 PM
        return 10 <= row['hour'] < 17 or (row['hour'] == 17 and row['minute'] == 0)

if __name__ == "__main__":
    df = pd.read_csv('cordGraph.csv')

    # Collect raw datetime (ignore our weekday column because it will be determined later)
    df['datetime_raw'] = pd.to_datetime(
        '2025 ' + df['Month'] + ' ' + df['day'].astype(str) + ' ' + df['time'],
        format='%Y %b %d %H:%M:%S',
        errors='coerce'
    )

    # Drop rows with invalid datetime
    df = df.dropna(subset=['datetime_raw'])

    # Correct for timezone offset (data is 3hrs 45mins ahead)
    df['datetime_est'] = df['datetime_raw'] - pd.Timedelta(hours=3, minutes=45)

    # Apply DST correction (data is in EST)
    eastern = pytz.timezone('America/New_York')
    df['datetime_est_dst'] = df['datetime_est'].apply(
        lambda dt: eastern.localize(dt, is_dst=False)
    )

    # Extract weekday, hour, minute
    df['weekday'] = df['datetime_est_dst'].dt.day_name().str[:3]
    df['hour'] = df['datetime_est_dst'].dt.hour
    df['minute'] = df['datetime_est_dst'].dt.minute

    # returns false for the within_valid_hours function
    df['within_hours'] = df.apply(within_valid_hours, axis=1)


    # filters out all data outside of rec hours
    df_valid = df[df['within_hours']].copy()

    # Convert occupancy to numeric
    df_valid['occupancy'] = pd.to_numeric(df_valid['occupancy'], errors='coerce')

## -------------------------------------------------------------
# Plotting

    # by day of week
    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    df_valid['weekday'] = pd.Categorical(df_valid['weekday'], categories=weekday_order, ordered=True)
    weekday_avg = df_valid.groupby('weekday', observed=False)['occupancy'].mean()
    weekday_avg = weekday_avg.reindex(weekday_order)

    df_valid['day_type'] = df_valid['weekday'].apply(
        lambda x: 'Weekday' if x in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] else 'Weekend'
    )

    # Gets the time in minutes since the start of the day
    df_valid['daily_time'] = (df['hour'] * 60.0 + df['minute']) / 60.0

    # Gives an average occupancy every half hour by day type
    quarterly_by_type = df_valid.groupby(['day_type', 'daily_time'])['occupancy'].mean().unstack(level=0)

    # Subtracts the previous row by the current row (the difference)
    slopes = quarterly_by_type.diff()

    # Dividing by the interval between rows (0.25) to get the rise over run (slope)
    slopes['Weekend'] = slopes['Weekend'].apply(lambda x: x / 0.25)
    slopes['Weekday'] = slopes['Weekday'].apply(lambda x: x / 0.25)

    plt.figure(figsize=(12, 6))
    if 'Weekday' in slopes.columns:
        plt.plot(slopes.index, slopes['Weekday'], 
                 marker='o', linewidth=2, label='Weekday', markersize=6)
    if 'Weekend' in slopes.columns:
        plt.plot(slopes.index, slopes['Weekend'], 
                 marker='s', linewidth=2, label='Weekend', markersize=6)
    plt.xlabel('Hour of Day')
    plt.ylabel('Change in Average Occupancy')
    plt.title('Change in Average Occupancy: Weekday vs Weekend')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.show()

    # Recording the day of each date time
    df_valid['date'] = df_valid['datetime_est_dst'].apply(
        lambda dt: dt.date()
    )

    # Averaging daily occupancy
    daily_means = df_valid.groupby(['date'])['occupancy'].mean()
    daily_medians = df_valid.groupby(['date'])['occupancy'].median()

    plt.plot(daily_means.index, daily_means.values,
             marker='.', linewidth=0, label='mean', color='r')
    plt.plot(daily_medians.index, daily_medians.values,
             marker='.', linewidth=0, label='median', color='b')
    plt.xlabel('Time')
    plt.ylabel('Daily Average Occupancy')
    plt.title('Daily Average Occupancy over time')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

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

    # all hourly data points
    plt.figure(figsize=(12, 6))
    if 'Weekday' in quarterly_by_type.columns:
        plt.plot(quarterly_by_type.index, quarterly_by_type['Weekday'], 
                 marker='o', linewidth=2, label='Weekday', markersize=6)
    if 'Weekend' in quarterly_by_type.columns:
        plt.plot(quarterly_by_type.index, quarterly_by_type['Weekend'], 
                 marker='s', linewidth=2, label='Weekend', markersize=6)
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Occupancy')
    plt.title('Average Occupancy: Weekday vs Weekend')
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

    print(f"\nBy Day Type:")
    print(df_valid.groupby('day_type')['occupancy'].agg(['mean', 'median', 'max']))

    print(f"\nBusiest Hours (Top 5):")
    print(hourly_avg.sort_values(ascending=False).head())

    print(f"\nBusiest Days (Top 3):")
    print(weekday_avg.sort_values(ascending=False).head(3))

    print("\n========================\n")

    print("df_valid\n", df_valid.describe(), "\n")
    print("quarterly\n", quarterly_by_type.describe(), "\n")
    print("slopes\n", slopes.describe(), "\n")


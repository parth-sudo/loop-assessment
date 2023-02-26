import random
import string
import pandas as pd
from .models import MyCSVFile
from datetime import datetime, timedelta
import pytz

#utility function to generate report.
def generate_report_util(store_status_csv_path, menu_hours_csv_path, timezone_csv_path):
    # Read CSV files
    store_status = pd.read_csv(store_status_csv_path)
    menu_hours = pd.read_csv(menu_hours_csv_path)
    timezones = pd.read_csv(timezone_csv_path)

    # Merge dataframes on store_id
    df = pd.merge(store_status, menu_hours, on='store_id')
    df = pd.merge(df, timezones, on='store_id')

    # Convert timestamp_utc column to datetime and set timezone
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc']).dt.tz_convert('UTC')

    # Convert start_time_local and end_time_local columns to timedelta
    df['start_time_local'] = pd.to_timedelta(df['start_time_local'])
    df['end_time_local'] = pd.to_timedelta(df['end_time_local'])

    # Convert timezone_str column to timezone object
    df['timezone'] = df['timezone_str'].apply(pytz.timezone)

    # Get current UTC time
    now_utc = datetime.now(tz=pytz.utc)

    # define time ranges
    last_hour_end = now_utc - timedelta(minutes=now_utc.minute, seconds=now_utc.second, microseconds=now_utc.microsecond)
    last_hour_start = last_hour_end - timedelta(hours=1)
    last_day_end = now_utc - timedelta(hours=now_utc.hour, minutes=now_utc.minute, seconds=now_utc.second, microseconds=now_utc.microsecond)
    last_day_start = last_day_end - timedelta(days=1)
    last_week_end = now_utc - timedelta(hours=now_utc.hour, minutes=now_utc.minute, seconds=now_utc.second, microseconds=now_utc.microsecond)
    last_week_start = last_week_end - timedelta(weeks=1)

    #correct till here.

    # filter data for each time range
    last_hour_df = df[df['timestamp_utc'].between(last_hour_start, last_hour_end)]
    last_day_df = df[df['timestamp_utc'].between(last_day_start, last_day_end)]
    last_week_df = df[df['timestamp_utc'].between(last_week_start, last_week_end)]

    print(last_day_df)

    # calculate uptime and downtime for each time range
    uptime_last_hour = last_hour_df[last_hour_df['status'] == 'active']
    downtime_last_hour = last_hour_df[last_hour_df['status'] == 'inactive']
    uptime_last_day = last_day_df[last_day_df['status'] == 'active']
    downtime_last_day = last_day_df[last_day_df['status'] == 'inactive']
    uptime_last_week = last_week_df[last_week_df['status'] == 'active']
    downtime_last_week = last_week_df[last_week_df['status'] == 'inactive']

    # calculate uptime and downtime percentages for each time range
    uptime_pct_last_hour = len(uptime_last_hour) / len(last_hour_df) if len(last_hour_df) > 0 else 0
    downtime_pct_last_hour = len(downtime_last_hour) / len(last_hour_df) if len(last_hour_df) > 0 else 0
    uptime_pct_last_day = len(uptime_last_day) / len(last_day_df) if len(last_day_df) > 0 else 0
    downtime_pct_last_day = len(downtime_last_day) / len(last_day_df) if len(last_day_df) > 0 else 0
    uptime_pct_last_week = len(uptime_last_week) / len(last_week_df) if len(last_week_df) > 0 else 0
    downtime_pct_last_week = len(downtime_last_week) / len(last_week_df) if len(last_week_df) > 0 else 0

    # create report dataframe
    report_df = pd.DataFrame({
        'uptime_last_hour': [uptime_pct_last_hour],
        'uptime_last_day': [uptime_pct_last_day],
        'uptime_last_week': [uptime_pct_last_week],
        'downtime_last_hour': [downtime_pct_last_hour],
        'downtime_last_day': [downtime_pct_last_day],
        'downtime_last_week': [downtime_pct_last_week]
    }, index=[df['store_id'][0]])

    # rename the index column
    report_df.index.names = ['store_id']

    # display report

    print(report_df)
    return report_df

# Random string generator.
def random_string_generator():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(10))


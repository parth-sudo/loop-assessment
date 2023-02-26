import random
import string

from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
from .models import MyCSVFile


def generate_report_util(store_status_path, menu_hours_path, timezone_path):

    # Read in the CSV files as dataframes
    store_status_df = pd.read_csv(store_status_path)
    menu_hours_df = pd.read_csv(menu_hours_path)
    timezone_df = pd.read_csv(timezone_path)

    # Merge the menu_hours and timezone dataframes on store_id
    menu_timezone_df = pd.merge(menu_hours_df, timezone_df, on='store_id')

    # Convert the timestamp_utc column in store_status_df to a datetime object
    store_status_df['timestamp_utc'] = pd.to_datetime(store_status_df['timestamp_utc'])

    # Convert the start_time_local and end_time_local columns in menu_timezone_df to timedelta objects
    menu_timezone_df['start_time_local'] = pd.to_timedelta(menu_timezone_df['start_time_local'])
    menu_timezone_df['end_time_local'] = pd.to_timedelta(menu_timezone_df['end_time_local'])

    # Get the current time in UTC
    current_time_utc = datetime.utcnow()

    # Group store_status_df by store_id and the hour of the timestamp_utc column
    store_status_hourly_grouped = store_status_df.groupby(['store_id', store_status_df['timestamp_utc'].dt.hour])

    # Calculate the uptime and downtime for the last hour
    uptime_last_hour = []
    downtime_last_hour = []
    for store_id, hour in store_status_hourly_grouped.groups.keys():
        hour_start_utc = current_time_utc.replace(hour=hour, minute=0, second=0, microsecond=0) - timedelta(hours=1)
        hour_end_utc = current_time_utc.replace(hour=hour, minute=0, second=0, microsecond=0)
        hour_statuses = store_status_hourly_grouped.get_group((store_id, hour))
        last_status = hour_statuses.tail(1)['status'].values[0]
        if last_status == 'active':
            uptime_last_hour.append((store_id, (hour_end_utc - hour_start_utc).total_seconds() // 60))
            downtime_last_hour.append((store_id, 0))
        else:
            uptime_last_hour.append((store_id, 0))
            downtime_last_hour.append((store_id, (hour_end_utc - hour_start_utc).total_seconds() // 60))

    # Group store_status_df by store_id and the day of the timestamp_utc column
    store_status_daily_grouped = store_status_df.groupby(['store_id', store_status_df['timestamp_utc'].dt.date])

    # Calculate the uptime and downtime for the last day
    uptime_last_day = []
    downtime_last_day = []
    for store_id, day in store_status_daily_grouped.groups.keys():
        day_start_utc = current_time_utc.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        day_end_utc = current_time_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        day_statuses = store_status_daily_grouped.get_group((store_id, day))
        last_status = day_statuses.tail(1)['status'].values[0]
        if last_status == 'active':
            uptime_last_day.append((store_id, (day_end_utc - day_start_utc).total_seconds() // 3600))
            downtime_last_day.append((store_id, 0))
        else:
            uptime_last_day.append((store_id, 0))
            downtime_last_day.append((store_id, (day_end_utc - day_start_utc).total_seconds() // 3600))
    store_status_weekly_grouped = store_status_df.groupby(['store_id', store_status_df['timestamp_utc'].dt.week])

    # Calculate the update time for the last week
    update_last_week = []
    for store_id, week in store_status_weekly_grouped.groups.keys():
        week_start_utc = current_time_utc.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(weeks=1)
        week_end_utc = current_time_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        week_statuses = store_status_weekly_grouped.get_group((store_id, week))
        num_updates = week_statuses[week_statuses['status'] == 'update'].shape[0]
        update_last_week.append((store_id, num_updates))

    # Merge the uptime and downtime dataframes
    uptime_df = pd.DataFrame(uptime_last_hour + uptime_last_day + uptime_last_week, columns=['store_id', 'uptime'])
    uptime_df = uptime_df.groupby('store_id').sum().reset_index()
    downtime_df = pd.DataFrame(downtime_last_hour + downtime_last_day + downtime_last_week, columns=['store_id', 'downtime'])
    downtime_df = downtime_df.groupby('store_id').sum().reset_index()

    # Merge the uptime, downtime, and update dataframes
    report_df = pd.merge(uptime_df, downtime_df, on='store_id')
    report_df = pd.merge(report_df, pd.DataFrame(update_last_week, columns=['store_id', 'updates']), on='store_id')

    # Convert the uptime and downtime columns to minutes and hours, respectively
    report_df['uptime_last_hour'] = report_df['uptime'].astype('int')
    report_df['uptime_last_day'] = report_df['uptime'] // 60
    report_df['downtime_last_hour'] = report_df['downtime'].astype('int')
    report_df['downtime_last_day'] = report_df['downtime'] // 60
    report_df['update_last_week'] = report_df['updates']

    # Drop the unnecessary columns
    report_df = report_df.drop(['uptime', 'downtime', 'updates'], axis=1)

    return report_df


def random_string_generator():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(10))


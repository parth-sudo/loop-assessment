from django.shortcuts import render
from django.http import HttpResponse
from .extras import random_string_generator, generate_report_util
from .models import Report, MyCSVFile

import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
import asyncio

def generate_report():
    # Load CSV files into pandas dataframes
    store_status_csv_path = MyCSVFile.objects.get(name='store_status').file.path
    menu_hours_csv_path = MyCSVFile.objects.get(name='menu_hours').file.path 
    timezone_csv_path = MyCSVFile.objects.get(name='timezones').file.path

    return generate_report_util(store_status_csv_path, menu_hours_csv_path, timezone_csv_path)

def trigger_report(request):

    if request.method == "GET":
        # Generate report id
        random_string = ""
        while True:
            random_string = random_string_generator()
            if not Report.objects.filter(report_id=random_string).exists():
                break

        # Store status against report id as 'Running' in DB
        print(random_string)
        report = Report(report_id=random_string, status="Running")
        report.save()

        # Generate report and store it as a CSV file
        # loop = asyncio.get_event_loop()
        # task = loop.create_task(generate_report())
        report_data = generate_report() 
        # report_data = await asyncio.wait_for(task, timeout=None)
        # report_df = pd.DataFrame.from_dict(report_data, orient='index')
        # report_csv_path = f"{random_string}.csv"
        # report_df.to_csv(report_csv_path)
        print(report_data.head(10))

        # Update status against report id as 'Complete' in DB
        Report.objects.filter(report_id=random_string).update(status="Complete")

        # Return response 200
        return HttpResponse("Response OK, Generating report")

    return HttpResponse("Invalid request.")


# /get_report endpoint
def get_report(request, report_id):

    # report_id = request[data]["report_id"]
    # Check status against report_id in DB
    if not Report.objects.filter(report_id=report_id).exists():
        return HttpResponse("Object not found", status=404)
    
    status = Report.objects.get(report_id=report_id).status
    if status == 'Running':
        return HttpResponse("Running")
    #   return 'Running', 200
    # Download CSV for report_id
    latest_csv = MyCSVFile.objects.latest('uploaded_at')
    # return 'Complete' and download the csv.
    return HttpResponse("200 ok")


from django.shortcuts import render
from django.http import HttpResponse
from .extras import random_string_generator, generate_report_util
from .models import Report, MyCSVFile
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
import asyncio
import tempfile
import os

from django.core.files import File
from tempfile import NamedTemporaryFile


from rest_framework.decorators import api_view


def generate_report():
    # Load CSV files into pandas dataframes
    store_status_csv_path = MyCSVFile.objects.get(name='store_status').file.path
    menu_hours_csv_path = MyCSVFile.objects.get(name='menu_hours').file.path 
    timezone_csv_path = MyCSVFile.objects.get(name='timezones').file.path

    return generate_report_util(store_status_csv_path, menu_hours_csv_path, timezone_csv_path)


@api_view(['POST'])
def trigger_report(request):

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
    report_data = generate_report()

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        report_data.to_csv(temp_file)
        temp_file.flush()
        temp_file.seek(0)
        new_name = f'new_report_csv-{random_string}'
        file_obj = MyCSVFile(name=new_name, report_id=random_string)
        file_obj.file.save(new_name, File(temp_file))

    # Update status against report id as 'Complete' in DB
    Report.objects.filter(report_id=random_string).update(status="Complete")

    # Return response 200
    return HttpResponse(f"Response OK, Report generated with ID: {random_string}" )



# /get_report endpoint
@api_view(['GET'])
def get_report(request, report_id):

  
    # Edge case
    if not Report.objects.filter(report_id=report_id).exists():
        return HttpResponse("Object not found", status=404)
    
    #Check status against report_id in DB
    status = Report.objects.get(report_id=report_id).status
    if status == 'Running':
        return HttpResponse("Running")
  
    # Download CSV for report_id
    # latest_file = MyCSVFile.objects.get(report_id=report_id)
    # with latest_file.file.open(mode='r') as f:
    #     csv_content = f.read()
    # print(csv_content)

    # # Return the HTTP response
    # return HttpResponse(f"CSV with the report id {report_id} has been generated")
    latest_file = MyCSVFile.objects.get(report_id=report_id)
    response = HttpResponse(latest_file.file.read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(latest_file.name)
    return response


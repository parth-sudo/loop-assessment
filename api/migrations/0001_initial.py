# Generated by Django 3.2.2 on 2023-02-24 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyCSVFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='csv_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_id', models.CharField(max_length=10, unique=True)),
                ('status', models.CharField(choices=[('Running', 'Running'), ('Complete', 'Complete')], default='Running', max_length=10)),
            ],
        ),
    ]
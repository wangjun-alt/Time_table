# Generated by Django 3.0.6 on 2020-05-13 07:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjectapp', '0005_auto_20200513_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseinfo',
            name='course_times',
        ),
        migrations.AlterField(
            model_name='schedule',
            name='sche_datetime',
            field=models.DateField(default=datetime.datetime(2020, 5, 13, 15, 54, 35, 387114), verbose_name='日程日期'),
        ),
    ]
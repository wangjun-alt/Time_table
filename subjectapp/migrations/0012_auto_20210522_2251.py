# Generated by Django 2.0 on 2021-05-22 14:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjectapp', '0011_auto_20210522_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='sche_datetime',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 22, 22, 51, 31, 762753), verbose_name='日程日期'),
        ),
    ]

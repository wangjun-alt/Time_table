# Generated by Django 3.1.5 on 2021-04-26 13:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjectapp', '0008_auto_20210425_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicuser',
            name='firstdays',
            field=models.DateField(default=datetime.date(2021, 4, 26), verbose_name='开学第一天'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='sche_datetime',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 26, 21, 23, 19, 732077), verbose_name='日程日期'),
        ),
    ]

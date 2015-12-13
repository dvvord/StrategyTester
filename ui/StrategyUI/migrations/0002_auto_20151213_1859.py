# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('StrategyUI', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(default=b'none@email.here', max_length=50),
        ),
        migrations.AlterField(
            model_name='result',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 13, 18, 59, 54, 832000)),
        ),
    ]

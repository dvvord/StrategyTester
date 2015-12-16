from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime


class User(models.Model):
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)


class Data(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=260)


class Profile(models.Model):
    name = models.CharField(max_length=50)
    data = models.ForeignKey(Data)
    commission = models.FloatField()


class StrategyModel(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=260)
    def __unicode__(self):
        return unicode(self.name)


class Trade(models.Model):
    date = models.DateTimeField(default=datetime.now())
    equity = models.FloatField()
    profit = models.FloatField()


class Result(models.Model):
    strategy = models.ForeignKey(StrategyModel)
    date = models.DateTimeField(default=datetime.now())
    profit = models.FloatField()

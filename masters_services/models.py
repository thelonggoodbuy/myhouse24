from django.db import models

from users.models import User
from appartments.models import Appartment


class MastersRequest(models.Model):
    REQUEST_TO = (
        ('electrician', 'электри'),
        ('plumber', 'сантехник'),
        ('locksmith', 'слесарь'),
    )
    MASTER_REQUEST_STATUS = (
        ('new', 'ноывая'),
        ('is_performing', 'в работе'),
        ('have_done', 'выполнена'),
    )
    master_type = models.CharField(max_length=200, choices=REQUEST_TO)
    master = models.ForeignKey(User, on_delete=models.CASCADE)
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    date_work = models.DateField()
    time_work = models.TimeField()
    desctiption = models.TextField()
    status = models.CharField(max_length=200, choices=MASTER_REQUEST_STATUS)
    admin_comment = models.TextField()
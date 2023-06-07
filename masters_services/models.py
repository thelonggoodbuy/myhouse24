from django.db import models

from users.models import User
from appartments.models import Appartment


class MastersRequest(models.Model):
    REQUEST_TO = (
        ('electrician', 'электрик'),
        ('plumber', 'сантехник'),
        ('locksmith', 'слесарь'),
        ('any_specialist', 'любой специалист'),
    )
    MASTER_REQUEST_STATUS = (
        ('new', 'новая'),
        ('is_performing', 'в работе'),
        ('have_done', 'выполнена'),
    )
    master_type = models.CharField(max_length=200, choices=REQUEST_TO)
    master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='masters_request', blank=True, null=True)
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    date_work = models.DateField()
    time_work = models.TimeField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=200, choices=MASTER_REQUEST_STATUS)
    admin_comment = models.TextField(blank=True, null=True)

    @classmethod
    def get_request_to_dictionary(cls):
        request_dictionary = {}
        for request_type in cls.REQUEST_TO: request_dictionary[request_type[0]] = request_type[1]
        return request_dictionary
    

    @classmethod
    def get_status_dictionary(cls):
        status_dictionary = {}
        for request_status in cls.MASTER_REQUEST_STATUS: status_dictionary[request_status[0]] = request_status[1]
        return status_dictionary
    

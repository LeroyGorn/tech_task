from django.contrib.auth.models import User
from django.db import models


class DataSchema(models.Model):
    class StatusChoices(models.TextChoices):
        generated = "Not Generated", "Not Generated"
        processing = "Processing", "Processing"
        ready = "Ready", "Ready"

    owner = models.ForeignKey(User, related_name="user_schemas", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    column_separator = models.CharField(max_length=3)
    string_character = models.CharField(max_length=3)
    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.generated)
    file = models.FileField(upload_to="files/", null=True, blank=True)
    filename = models.CharField(max_length=64, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(null=True, auto_now=True)

    def get_file_link(self):
        return f"/files/{self.filename}"


class DataColumn(models.Model):
    class ColumnChoices(models.TextChoices):
        full_name = "Full Name", "Full Name"
        job = "Job", "Job"
        email = "Email", "Email"
        domain_name = "Domain Name", "Domain Name"
        phone_number = "Phone Number", "Phone Number"
        company_name = "Company Name", "Company Name"
        text = "Text", "Text"
        integer = "Integer", "Integer"
        address = "Address", "Address"
        date = "Date", "Date"

    columns = models.ForeignKey(DataSchema, related_name="data_column", on_delete=models.CASCADE)
    column_type = models.CharField(max_length=64, choices=ColumnChoices.choices)
    column_name = models.CharField(max_length=255)
    from_value = models.PositiveSmallIntegerField(null=True, blank=True)
    to_value = models.PositiveSmallIntegerField(null=True, blank=True)
    order = models.SmallIntegerField()

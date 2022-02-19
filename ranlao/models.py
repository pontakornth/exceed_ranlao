from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Table(models.Model):
    """Table at the pub and its status."""
    table_number = models.IntegerField(validators=[MinValueValidator(1)], null=False, unique=True)
    # is_calling: Call the staff.
    is_calling = models.BooleanField(default=False, null=False)


class VisitorLog(models.Model):
    """Log of visitor by hour."""
    log_time = models.DateTimeField(null=False)
    amount = models.IntegerField(validators=[MinValueValidator(0)], null=False, default=0)

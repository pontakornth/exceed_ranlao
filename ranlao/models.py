from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Table(models.Model):
    table_number = models.IntegerField(validators=[MinValueValidator(1)], null=False, unique=True)
    # is_calling: Call the staff.
    is_calling = models.BooleanField(default=False, null=False)

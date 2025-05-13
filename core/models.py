import uuid
from django.db import models

class Transfer(models.Model):
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # UUID for file ID
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

from django.db import models
from django.utils import timezone
import uuid

# Create your models here.

class GameRoom(models.Model):
    room_code = models.CharField(max_length=10, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    max_players = models.PositiveSmallIntegerField(default=2)
    
    def is_expired(self):
        return timezone.now() >= self.expires_at
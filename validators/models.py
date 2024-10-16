
from django.db import models
from django.contrib.postgres.fields import ArrayField
import logging

        

class HotkeyModel(models.Model):
    hotkey = models.CharField(max_length=255)  # Adjust max_length as needed
    stake = models.FloatField()  # or IntegerField, based on your needs

    def __str__(self):
        # Customize this string to display what you want in the dropdown
        return f"{self.hotkey} (Stake: {self.stake})"
    def __eq__(self, other):
        return (self.hotkey == other.hotkey)

    def __hash__(self):
        return hash((self.hotkey))

class ChildHotkeyModel(models.Model):
    parent = models.ForeignKey(HotkeyModel, related_name='parent_hotkey', on_delete=models.CASCADE)
    child = models.ForeignKey(HotkeyModel, related_name='child_hotkey', on_delete=models.CASCADE)
    proportion = models.FloatField()
    netuid = models.IntegerField()

    def __str__(self):
        return f"Child: {self.child}, Parent: {self.parent}, NetUID: {self.netuid}"

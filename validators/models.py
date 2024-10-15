# from django.db import models

# class Validator(models.Model):
#     coldkey = models.CharField(max_length=255)
#     hotkey = models.CharField(max_length=255, unique=True)
#     stake = models.FloatField()
#     parentkey_netuids = models.JSONField(default=list)
#     childkeys = models.JSONField(default=list)
#     parentkeys = models.JSONField(default=list)

#     def __str__(self):
#         return self.hotkey

# from django.db import models
# from django.contrib.postgres.fields import ArrayField

# class Validators(models.Model):
#     coldkey = models.CharField(max_length=255)
#     hotkey = models.CharField(max_length=255, unique=True)
#     stake = models.FloatField()
#     parentkey_netuids = ArrayField(models.IntegerField(), default=list, blank=True)
#     childkeys = models.JSONField(default=list, blank=True)
#     parentkeys = models.JSONField(default=list, blank=True)

#     def __eq__(self, other):
#         if isinstance(other, Validators):
#             return (self.coldkey == other.coldkey and
#                     self.hotkey == other.hotkey)
#         return False

#     def __hash__(self):
#         return hash((self.coldkey, self.hotkey))
    
#     def add_parentkeys(self, parent_hotkey, proportion, net_uid):
#         # Method to add a parentkey dictionary to the parentkeys list
#         parentkey_info = {
#             'parent_key': parent_hotkey,
#             'proportion': proportion,
#             'net_uid': net_uid
#         }
#         self.parentkeys.append(parentkey_info)
#         self.save(update_fields=['parentkeys'])
        
#     def add_childkeys(self, child_hotkey, proportion, net_uid):
#         # Method to add a childkey dictionary to the childkeys list
#         childkey_info = {
#             'child_hotkey': child_hotkey,
#             'proportion': proportion,
#             'net_uid': net_uid
#         }
#         self.childkeys.append(childkey_info)
#         self.save(update_fields=['childkeys'])

#     def __str__(self):
#         return self.hotkey
from django.db import models
from django.contrib.postgres.fields import ArrayField
import json
import logging

class Validators(models.Model):
    coldkey = models.CharField(max_length=255)
    hotkey = models.CharField(max_length=255, unique=True)
    stake = models.FloatField()
    parentkey_netuids = models.JSONField(default=list, blank=True)
    childkeys = models.JSONField(default=list, blank=True)
    parentkeys = models.JSONField(default=list, blank=True)

    def __eq__(self, other):
        return (self.coldkey == other.coldkey and self.hotkey == other.hotkey)

    def __hash__(self):
        return hash((self.coldkey, self.hotkey))

    def add_parentkeys(self, parent_hotkey, proportion, net_uid):
        parentkey_info = {
            'parent_key': parent_hotkey,
            'proportion': proportion,
            'net_uid': net_uid
        }
        self.parentkeys.append(parentkey_info)
        logging.debug(f"Saving validator with parentkeys: {self.parentkeys}")
        if self.pk:  # Check if the instance has a primary key
            self.save(update_fields=['parentkeys'])
        else:
            self.save()

    def add_childkeys(self, child_hotkey, proportion, net_uid):
        childkey_info = {
            'child_hotkey': child_hotkey,
            'proportion': proportion,
            'net_uid': net_uid
        }
        self.childkeys.append(childkey_info)
        logging.debug(f"Saving validator with childkeys: {self.childkeys}")
        if self.pk:  # Check if the instance has a primary key
            self.save(update_fields=['childkeys'])
        else:
            self.save()

    def get_parentkey_netuids(self):
        # Deserialize parentkey_netuids from JSON
        if isinstance(self.parentkey_netuids, str):
            return json.loads(self.parentkey_netuids)
        return self.parentkey_netuids

    def __str__(self):
        return self.hotkey

from django.db import models
from django.contrib.postgres.fields import ArrayField
import json
import logging

# class Validators(models.Model):
#     coldkey = models.CharField(max_length=255)
#     hotkey = models.CharField(max_length=255, unique=True)
#     stake = models.FloatField()
#     validator_installed_netuids = models.JSONField(default=list, blank=True)
#     childkeys = models.JSONField(default=list, blank=True)
#     parentkeys = models.JSONField(default=list, blank=True)

#     def __eq__(self, other):
#         return (self.coldkey == other.coldkey and self.hotkey == other.hotkey)

#     def __hash__(self):
#         return hash((self.coldkey, self.hotkey))

#     def add_parentkeys(self, parent_hotkey, proportion, net_uid):
#         parentkey_info = {
#             'parent_key': parent_hotkey,
#             'proportion': proportion,
#             'net_uid': net_uid
#         }
#         self.parentkeys.append(parentkey_info)
#         logging.debug(f"Saving validator with parentkeys: {self.parentkeys}")
#         if self.pk:  # Check if the instance has a primary key
#             self.save(update_fields=['parentkeys'])
#         else:
#             self.save()

#     def add_childkeys(self, child_hotkey, proportion, net_uid):
#         childkey_info = {
#             'child_hotkey': child_hotkey,
#             'proportion': proportion,
#             'net_uid': net_uid
#         }
#         self.childkeys.append(childkey_info)
#         logging.debug(f"Saving validator with childkeys: {self.childkeys}")
#         if self.pk:  # Check if the instance has a primary key
#             self.save(update_fields=['childkeys'])
#         else:
#             self.save()

#     def get_validator_installed_netuids(self):
#         # Deserialize validator_installed_netuids from JSON
#         if isinstance(self.validator_installed_netuids, str):
#             return json.loads(self.validator_installed_netuids)
#         return self.validator_installed_netuids

#     def __str__(self):
#         return self.hotkey



# class ValidatorChildKeyInfo(models.Model):
#     parent_hotkey = models.ForeignKey(Validators, to_field='hotkey', on_delete=models.CASCADE, related_name='child_keys', db_column='parent_hotkey')
#     parent_coldkey = models.CharField(max_length=255)
#     parent_stake = models.FloatField()
#     child_hotkey = models.CharField(max_length=255)
#     # child_stake = models.FloatField()
#     stake_proportion = models.FloatField()
#     subnet_uid = models.IntegerField()

#     class Meta:
#         unique_together = ('parent_hotkey', 'child_hotkey', 'subnet_uid')
        

class HotkeyModel(models.Model):
    stake = models.FloatField()  # or IntegerField, based on your needs
    hotkey = models.CharField(max_length=255)  # Adjust max_length as needed

    def __str__(self):
        # Customize this string to display what you want in the dropdown
        return f"{self.hotkey} (Stake: {self.stake})"
    def __eq__(self, other):
        return (self.hotkey == other.hotkey)

    def __hash__(self):
        return hash((self.hotkey))

class ChildHotkeyModel(models.Model):
    child = models.ForeignKey(HotkeyModel, related_name='child_hotkey', on_delete=models.CASCADE)
    parent = models.ForeignKey(HotkeyModel, related_name='parent_hotkey', on_delete=models.CASCADE)
    netuid = models.IntegerField()
    proportion = models.FloatField()

    def __str__(self):
        return f"Child: {self.child}, Parent: {self.parent}, NetUID: {self.netuid}"

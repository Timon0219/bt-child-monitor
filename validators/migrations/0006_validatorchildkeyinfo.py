# Generated by Django 5.1.2 on 2024-10-15 01:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0005_alter_validators_parentkey_netuids'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValidatorChildKeyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_coldkey', models.CharField(max_length=255)),
                ('parent_stake', models.FloatField()),
                ('child_hotkey', models.CharField(max_length=255)),
                ('child_stake', models.FloatField()),
                ('stake_proportion', models.FloatField()),
                ('subnet_uid', models.IntegerField()),
                ('parent_hotkey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_keys', to='validators.validators', to_field='hotkey')),
            ],
            options={
                'unique_together': {('parent_hotkey', 'child_hotkey', 'subnet_uid')},
            },
        ),
    ]

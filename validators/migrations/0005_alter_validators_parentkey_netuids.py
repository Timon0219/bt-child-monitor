# Generated by Django 5.1.2 on 2024-10-14 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0004_alter_validators_parentkey_netuids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validators',
            name='parentkey_netuids',
            field=models.JSONField(blank=True, default=list),
        ),
    ]

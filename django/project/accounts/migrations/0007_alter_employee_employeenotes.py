# Generated by Django 4.0.3 on 2022-05-20 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_grant_rights'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='employeeNotes',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]

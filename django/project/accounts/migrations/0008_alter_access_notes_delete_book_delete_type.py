# Generated by Django 4.0.3 on 2022-05-20 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_employee_employeenotes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='access',
            name='notes',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Book',
        ),
        migrations.DeleteModel(
            name='Type',
        ),
    ]
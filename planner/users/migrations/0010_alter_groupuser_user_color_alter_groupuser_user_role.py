# Generated by Django 5.1.4 on 2025-04-17 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_userprofile_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupuser',
            name='user_color',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='groupuser',
            name='user_role',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]

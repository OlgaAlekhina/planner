# Generated by Django 5.1.4 on 2025-03-16 22:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_eventmeta_bymonth_eventmeta_byweekno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventmeta',
            name='byweekno',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='CanceledEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancel_date', models.DateField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
    ]

# Generated by Django 3.1.2 on 2020-12-26 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customcalendar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ccalendar',
            name='currentday',
            field=models.IntegerField(default=1, verbose_name='Current Day'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ccalendar',
            name='currentmonth',
            field=models.IntegerField(default=1, verbose_name='Current Month'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ccalendar',
            name='currentyear',
            field=models.IntegerField(default=0, verbose_name='Current Year'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cweekday',
            name='workday',
            field=models.BooleanField(default=True, verbose_name='Workday'),
        ),
    ]
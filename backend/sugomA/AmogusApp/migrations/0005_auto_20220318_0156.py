# Generated by Django 3.2.11 on 2022-03-17 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AmogusApp', '0004_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='contractAddress',
            field=models.TextField(null=True, verbose_name='contractAddress'),
        ),
        migrations.AddField(
            model_name='room',
            name='publicName',
            field=models.TextField(null=True, verbose_name='publicName'),
        ),
    ]

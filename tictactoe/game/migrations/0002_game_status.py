# Generated by Django 5.1.3 on 2024-11-13 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='status',
            field=models.CharField(choices=[('WAITING', 'Waiting for another player'), ('IN_PROGRESS', 'Game in progress'), ('FINISHED', 'Game finished')], default='WAITING', max_length=15),
        ),
    ]

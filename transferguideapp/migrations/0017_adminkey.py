# Generated by Django 4.1.6 on 2023-04-16 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0016_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=256)),
            ],
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-30 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0003_rename_property_message_related_property_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='related_property',
            new_name='property',
        ),
        migrations.AlterField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

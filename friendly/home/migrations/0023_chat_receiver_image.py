# Generated by Django 5.0.6 on 2024-06-17 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='receiver_image',
            field=models.ImageField(blank=True, null=True, upload_to='chat/images/'),
        ),
    ]

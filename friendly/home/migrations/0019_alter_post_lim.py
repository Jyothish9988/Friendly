# Generated by Django 5.0.6 on 2024-06-16 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_alter_friendrequest_from_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='lim',
            field=models.CharField(choices=[('new', 'new'), ('yes', 'Yes'), ('no', 'No')], default='', max_length=20),
        ),
    ]
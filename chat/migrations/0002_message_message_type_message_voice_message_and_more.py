# Generated by Django 5.0.6 on 2024-11-12 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='message_type',
            field=models.CharField(choices=[('text', 'Text'), ('voice', 'Voice')], default='text', max_length=5),
        ),
        migrations.AddField(
            model_name='message',
            name='voice_message',
            field=models.FileField(blank=True, null=True, upload_to='voice_messages/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]

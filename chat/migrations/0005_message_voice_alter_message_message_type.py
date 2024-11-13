# Generated by Django 5.0.6 on 2024-11-12 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_remove_message_voice_message_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='voice',
            field=models.FileField(blank=True, null=True, upload_to='voice_messages/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='message_type',
            field=models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('voice', 'Voice')], default='text', max_length=5),
        ),
    ]
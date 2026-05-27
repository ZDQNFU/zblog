from django.db import migrations


def rename_human_to_user(apps, schema_editor):
    ChatMessage = apps.get_model('chat_robot', 'ChatMessage')
    ChatMessage.objects.filter(role='human').update(role='user')


def reverse_rename(apps, schema_editor):
    ChatMessage = apps.get_model('chat_robot', 'ChatMessage')
    ChatMessage.objects.filter(role='user').update(role='human')


class Migration(migrations.Migration):

    dependencies = [
        ('chat_robot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_human_to_user, reverse_rename),
    ]

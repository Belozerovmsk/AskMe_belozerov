# Generated by Django 4.2.1 on 2023-05-19 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askme', '0003_alter_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]

# Generated by Django 5.0.2 on 2024-03-06 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AscentFlowHub_API', '0007_treegoalsmodel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='treegoalsmodel',
            name='life_category',
            field=models.ManyToManyField(to='AscentFlowHub_API.lifecategorymodel'),
        ),
    ]

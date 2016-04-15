# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-16 20:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0002_auto_20151007_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blobtext',
            name='format',
            field=models.CharField(choices=[(' ', 'Plain text'), ('M', 'Markdown text'), ('<', 'HTML document'), ('B', 'Binary content')], default=' ', max_length=1),
        ),
        migrations.AlterField(
            model_name='permission',
            name='effect',
            field=models.CharField(choices=[('A', 'Allow'), ('D', 'Deny')], max_length=1),
        ),
        migrations.AlterField(
            model_name='permission',
            name='scope',
            field=models.CharField(choices=[('0', 'Public'), ('1', 'Staff'), ('2', 'Administrators'), ('G', 'Specify group'), ('U', 'Specify user')], max_length=1),
        ),
        migrations.AlterField(
            model_name='permission',
            name='type',
            field=models.CharField(choices=[('1', 'View document'), ('2', 'Comment on document'), ('3', 'Edit document')], max_length=1),
        ),
        migrations.AlterField(
            model_name='revision',
            name='type',
            field=models.CharField(choices=[('.', 'Local revision'), ('+', 'External linked file')], default='.', max_length=1),
        ),
    ]
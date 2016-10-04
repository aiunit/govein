# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-04 16:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BoardState',
            fields=[
                ('id', models.CharField(help_text='SHA1 hash for the board state', max_length=40, primary_key=True, serialize=False)),
                ('rob_x', models.SmallIntegerField(default=-1, verbose_name='Rob position x index')),
                ('rob_y', models.SmallIntegerField(default=-1, verbose_name='Rob position y index')),
                ('data', models.BinaryField(default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length=91)),
            ],
            options={
                'db_table': 'go_core_board_state',
                'verbose_name': 'Board State',
                'verbose_name_plural': 'Board States',
            },
        ),
    ]
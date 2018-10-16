# Generated by Django 2.0.6 on 2018-10-10 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.IntegerField(unique=True, verbose_name='节点id')),
                ('name', models.CharField(blank=True, max_length=30, null=True, verbose_name='节点名称')),
                ('ip', models.GenericIPAddressField(verbose_name='节点ip')),
            ],
        ),
    ]

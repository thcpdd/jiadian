# Generated by Django 4.1.7 on 2023-07-07 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_myuser_introduce_alter_myuser_phone"),
    ]

    operations = [
        migrations.AlterField(
            model_name="myuser",
            name="phone",
            field=models.CharField(max_length=11, null=True, verbose_name="手机号"),
        ),
    ]
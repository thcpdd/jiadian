# Generated by Django 4.1.7 on 2023-07-15 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_alter_address_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="myuser",
            name="image",
            field=models.ImageField(
                default="default.jpg", upload_to="user", verbose_name="用户头像"
            ),
        ),
    ]

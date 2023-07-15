# Generated by Django 4.1.7 on 2023-07-07 02:34

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="MyUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="修改时间"),
                ),
                ("is_delete", models.BooleanField(default=False, verbose_name="删除标记")),
                ("phone", models.IntegerField(verbose_name="手机号")),
                (
                    "introduce",
                    models.CharField(default="", max_length=100, verbose_name="个人介绍"),
                ),
                (
                    "balance",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=11, verbose_name="余额"
                    ),
                ),
                (
                    "total_recharge",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=11, verbose_name="累计充值"
                    ),
                ),
                (
                    "total_consumption",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=11, verbose_name="累计消费"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "用户表",
                "verbose_name_plural": "用户表",
                "db_table": "user_table",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="修改时间"),
                ),
                ("is_delete", models.BooleanField(default=False, verbose_name="删除标记")),
                ("recipient", models.CharField(max_length=12, verbose_name="收件人")),
                ("phone", models.IntegerField(verbose_name="手机号")),
                ("province", models.CharField(max_length=15, verbose_name="省份")),
                ("city", models.CharField(max_length=10, verbose_name="城市")),
                ("country", models.CharField(max_length=10, verbose_name="区/县")),
                (
                    "detail_address",
                    models.CharField(max_length=40, verbose_name="详细地址"),
                ),
                ("is_default", models.BooleanField(default=False, verbose_name="默认地址")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="所属用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "地址表",
                "verbose_name_plural": "地址表",
                "db_table": "address_table",
            },
        ),
    ]

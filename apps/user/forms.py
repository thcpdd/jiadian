from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext_lazy
from django import forms


class LoginForm(AuthenticationForm):
    """ 登录表单 """
    username = UsernameField(
        widget=forms.TextInput(attrs={
            "autofocus": True,
            "class": "input",
            "placeholder": " 请输入用户名...",
            'value': 'rainbow'
        }))
    password = forms.CharField(
        label=gettext_lazy("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": "input",
            "placeholder": " 请输入密码...",
            'value': 'rainbow'
        }),
    )

from django import forms
from goods.models import SsrAccount


class CreateAccountForm(forms.Form):
    username = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=True, min_length=3)

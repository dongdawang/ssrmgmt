from django import forms
from .models import UserProfile


class UploadProfilePhoto(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


class ModifyGeneralForm(forms.Form):
    gender = forms.CharField(required=True, min_length=6)
    birthday = forms.DateField(required=False, input_formats=['%Y-%m-%d'])
    address = forms.CharField(required=False, max_length=100)
    mobile = forms.CharField(required=False, max_length=11)


class ModifyUsernameForm(forms.Form):
    username = forms.CharField(required=True, max_length=150)


class ModifySSRForm(forms.Form):
    passwd = forms.CharField(required=False, max_length=30)
    method = forms.CharField(required=False, max_length=30)
    protocol = forms.CharField(required=False, max_length=30)
    obfs = forms.CharField(required=False, max_length=30)
    obfs_enable = forms.BooleanField(required=False)


class WorkOrderForm(forms.Form):
    title = forms.CharField(max_length=50)
    body = forms.CharField()

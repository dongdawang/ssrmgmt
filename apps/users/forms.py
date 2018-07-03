from django import forms
from .models import UserProfile


class UploadProfilePhoto(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


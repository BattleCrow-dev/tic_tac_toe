from .models import VoiceMessage

from django import forms
from django.contrib.auth.models import User

class SimpleRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

class VoiceMessageForm(forms.ModelForm):
    class Meta:
        model = VoiceMessage
        fields = ['audio_file']

from django import forms
from .models import Folder

class FolderForm(forms.ModelForm):
    # a form for folders
    class Meta:
        model = Folder
        fields = ['name', 'password']
        widgets = {
            'password': forms.PasswordInput() # a widget that renders the password field as a password input
        }

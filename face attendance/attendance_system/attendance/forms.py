from django import forms
from .models import User  # Ensure this is the correct import

class AddUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'name', 'phone_number', 'role', 'dob', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

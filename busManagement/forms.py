from django import forms
from .models import User

class UserSignupForm(forms.ModelForm):
    class Meta:
        model = User  # 'model' should be lowercase
        fields = ('username','email','password',)  # '__all__' should be a string, but the syntax is correct

class UserSignInForm(forms.ModelForm):  # Naming conventions - class name should be PascalCase
    class Meta:
        model = User
        fields = ('email','password',)  

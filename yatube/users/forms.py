from django.contrib.auth.forms import \
    UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Contact

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'body')


class SetPassword(SetPasswordForm):
    class Meta(PasswordChangeForm):
        fields = ('old_password', 'new_password1', 'new_password2')

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Käyttäjänimi'
        self.fields['email'].label = 'Sähköposti'
        self.fields['password1'].label = 'Salasana'
        self.fields['password2'].label = 'Salasana uudelleen'
        # Finnish help texts
        self.fields['username'].help_text = 'Enintään 150 merkkiä.'
        self.fields['password1'].help_text = 'Vähintään 8 merkkiä.'
        self.fields['password2'].help_text = 'Kirjoita sama salasana uudelleen.'

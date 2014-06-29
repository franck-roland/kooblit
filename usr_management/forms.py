from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserKooblit

class UserCreationForm(UserCreationForm):
    # password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    # password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)
    birthday = forms.DateField(label="Birthday")

    class Meta:
        model = UserKooblit
        # widgets = {
        #     'password': forms.PasswordInput(),
        # }
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 
                  'password2', 'birthday')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError("Password mismatch")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        import pdb;pdb.set_trace()
        if commit:
            user.save()
        return user
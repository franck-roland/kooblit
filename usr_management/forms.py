#--* coding: latin-1 *--
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserKooblit

        
class UserCreationFormKooblit(UserCreationForm):
    # password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    # password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)
    birthday = forms.DateField(label="Birthday", localize=True)
    email2 = forms.EmailField()

    class Meta:
        model = UserKooblit
        # widgets = {
        #     'password': forms.PasswordInput(),
        # }
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 
                  'password2', 'birthday', 'email2')

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name") 
        if not first_name:
            raise forms.ValidationError(u'Prenom obligatoire')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name") 
        if not last_name:
            raise forms.ValidationError(u'Nom obligatoire')
        return last_name

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError("Password mismatch")
        return password2
    
    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email and email2 and email2 != email:
            raise forms.ValidationError(u'Email addresses mismatch.')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'Cette adresse est deja utilisee')
        return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
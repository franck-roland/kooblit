#--* coding: utf-8 *--
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserKooblit, Address
from django.utils.translation import ugettext_lazy as _

class UserCreationFormKooblit(UserCreationForm):

    class Meta:
        model = UserKooblit
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            raise forms.ValidationError(u'Pseudo obligatoire')
        try:
            UserKooblit.objects.get(username__iexact=username)
            raise forms.ValidationError(u'Ce pseudo existe déjà')
        except UserKooblit.DoesNotExist:
            pass
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(u'Email obligatoire')
        try:
            UserKooblit.objects.get(email=email)
            raise forms.ValidationError(u'Cette adresse mail existe déjà')
        except UserKooblit.DoesNotExist:
            pass
        return email

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
            raise forms.ValidationError("Password mismatch")
        return password2

    def save(self, commit=True):
        user = super(UserCreationFormKooblit, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AddressChangeForm(ModelForm):

    class Meta:
        model = Address
        fields = (
                    'number',
                    'street_line1',
                    'street_line2',
                    'zipcode',
                    'city','country')
    
    def clean_number(self):
        number=self.cleaned_data.get("number")
        try:
            number = int(number)
        except Exception, e:
            raise forms.ValidationError(_("Le numéro doit être un nombre"))
        return number



class ReinitialisationForm(forms.Form):
    email = forms.EmailField()
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError(u'Champ obligatoire')
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError(u"Cette adresse n'existe pas")
        return email


class DoReinitialisationForm(forms.Form):
    mdp1 = forms.CharField(widget=forms.PasswordInput())
    mdp2 = forms.CharField(widget=forms.PasswordInput())

    def clean_mdp1(self):
        mdp1 = self.cleaned_data.get('mdp1')
        if not mdp1:
            raise forms.ValidationError(u'Champ obligatoire')
        return mdp1

    def clean_mdp2(self):
        mdp1 = self.cleaned_data.get('mdp1')
        mdp2 = self.cleaned_data.get('mdp2')
        if not mdp2:
            raise forms.ValidationError(u'Champ obligatoire')
        if mdp1 != mdp2:
            raise forms.ValidationError(u'Mot de passe différent')
        return mdp2

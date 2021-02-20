from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm

from .models import user_registrated

from .models import AdvUser, SubRubric, SuperRubric, Bulletin, AdditionalImage, Comment


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Username',
                                required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password',
                               required=True)


class ChangeUserProfileForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Username')

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='First name')

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Last name')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_massages')


class ChangeUserPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(required=True, label='Old password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    new_password1 = forms.CharField(required=True, label='New password 1', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    new_password2 = forms.CharField(required=True, label='New password 2', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Username', required=True)

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email', required=True)

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='First name',
                                                                                        required=False ,help_text='Not necessary')

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Last name',
                                                                                        required=False ,help_text='Not necessary')

    password1 = forms.CharField(required=True, label='Password 1',
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    password2 = forms.CharField(required=True, label='Password 2',
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))


    def clean_password1(self):
        password1 = self.cleaned_data['password1'] 
        if password1: 
            password_validation.validate_password(password1) 
        return password1


    def clean(self): 
        super().clean() 

        password1 = self.cleaned_data['password1'] 
        password2 = self.cleaned_data['password2'] 

        if password1 and password2 and password1 != password2: 
            errors = {'password2': ValidationError('Passwords do not match!', code='password _ mismatch ')}
            raise ValidationError(errors)


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        user.is_active = False
        user.is_activated = False

        if commit:
            user.save()

        user_registrated.send(UserRegistrationForm, instance=user)
        return user


    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 
                    'first_name', 'last_name', 'send_massages')


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email', required=True)


class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(),empty_label=None, required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=70, widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Search', 
        'aria-label':"Recipient's username", 'aria-describedby':'basic-addon2'}))


class BulletinForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    price = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    rubric = forms.ModelChoiceField(queryset=SubRubric.objects.all(), widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))

    contacts = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control' ,'type': 'file'}), label='Main image')

    class Meta:
        model = Bulletin
        widgets = {'author': forms.HiddenInput}
        exclude = ('is_active', 'published')


AdditionalImagesFormSet = inlineformset_factory(Bulletin, AdditionalImage, fields=('image', ), can_delete=False,
                                            widgets={'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'type': 'file'})})


class CommentForm(forms.ModelForm):

    content = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Comment
        exclude = ('created_at',)
        widgets = {'author': forms.HiddenInput, 'bulletin': forms.HiddenInput}

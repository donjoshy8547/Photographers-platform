"""
Django Forms for Accounts App
Clean, validated forms for user registration and profiles
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser, PhotographerProfile, ClientProfile, AssistantProfile, UserRole


class UserRegistrationForm(UserCreationForm):
    """User registration form with role selection"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    
    role = forms.ChoiceField(
        choices=UserRole.choices,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select your account type'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Base user profile form"""
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'bio', 
                  'city', 'country', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PhotographerProfileForm(forms.ModelForm):
    """Photographer-specific profile form"""
    
    specialties = forms.CharField(
        required=False,
        help_text='Comma-separated list (e.g., Wedding, Portrait, Event)'
    )
    
    class Meta:
        model = PhotographerProfile
        fields = ('specialties', 'years_experience', 'equipment_list',
                  'portfolio_url', 'instagram_url', 'hourly_rate',
                  'is_available', 'max_events_per_month')
        widgets = {
            'specialties': forms.TextInput(attrs={'class': 'form-control'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipment_list': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_events_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ClientProfileForm(forms.ModelForm):
    """Client profile form"""
    
    class Meta:
        model = ClientProfile
        fields = ('event_preferences', 'min_budget', 'max_budget')
        widgets = {
            'event_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'min_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class AssistantProfileForm(forms.ModelForm):
    """Assistant photographer profile form"""
    
    class Meta:
        model = AssistantProfile
        fields = ('supervising_photographer', 'skills', 'certifications', 'is_available')
        widgets = {
            'supervising_photographer': forms.Select(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LoginForm(forms.Form):
    """Login form"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
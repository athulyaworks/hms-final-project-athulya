from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from hospital.models import Patient
from django.db import IntegrityError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    age = forms.IntegerField(min_value=0)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    contact_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 
                  'age', 'gender', 'contact_number', 'address')



    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = 'patient'

        if commit:
            user.save()

            # Create patient profile only if not exists
            try:
                if not hasattr(user, 'patient_profile'):
                    Patient.objects.create(
                        user=user,
                        age=self.cleaned_data['age'],
                        gender=self.cleaned_data['gender'],
                        contact_number=self.cleaned_data['contact_number'],
                        address=self.cleaned_data['address'],
                    )
            except IntegrityError:
                # Optional: Handle duplicate creation
                pass

        return user
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email


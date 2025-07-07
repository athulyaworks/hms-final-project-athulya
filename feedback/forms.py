from django import forms
from .models import DoctorFeedback, HospitalFeedback

from django import forms
from .models import DoctorFeedback

class DoctorFeedbackForm(forms.ModelForm):
    class Meta:
        model = DoctorFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        help_texts = {
            'rating': 'Enter a rating between 1 (worst) and 5 (best).',
        }


class HospitalFeedbackForm(forms.ModelForm):
    class Meta:
        model = HospitalFeedback
        fields = ['feedback']

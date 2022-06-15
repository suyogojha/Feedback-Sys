from django import forms
from .models import Company, Feedback

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','tag_line','description',]


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['first_name','last_name','phone_number','comment']




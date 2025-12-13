from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 1, 'class': 'review-rating-input'}),
            'review_text': forms.Textarea(attrs={'rows': 4, 'class': 'review-textarea', 'placeholder': 'Write your review...'}),
        } 
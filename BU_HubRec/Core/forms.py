# Core/forms.py

from django import forms
from .models import Hub

class Step1Form(forms.Form):
    """Step 1: Hub Selection with counts"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically create checkbox fields for each Hub
        for hub in Hub.objects.all():
            field_name = f'hub_{hub.unit_name}'
            count_field_name = f'{field_name}_count'
            
            # Checkbox for hub selection
            self.fields[field_name] = forms.BooleanField(
                label=hub.get_unit_name_display(),
                required=False,
            )
            
            # Number input for how many courses needed
            self.fields[count_field_name] = forms.IntegerField(
                label=f'How many {hub.unit_name} courses needed?',
                min_value=1,
                max_value=10,
                initial=1,
                required=False,
                widget=forms.NumberInput(attrs={
                    'class': 'count-input',
                    'min': '1',
                    'max': '10',
                    'value': '1',
                    'id': f'id_{field_name}_count',
                })
            )
    
    def clean(self):
        """Custom validation to ensure checked hubs have counts"""
        cleaned_data = super().clean()
        
        for field_name, value in cleaned_data.items():
            if field_name.startswith('hub_') and not field_name.endswith('_count'):
                if value:  # If hub is checked
                    count_field_name = f'{field_name}_count'
                    count_value = cleaned_data.get(count_field_name)
                    
                    # If no count provided, default to 1
                    if not count_value:
                        cleaned_data[count_field_name] = 1
        
        return cleaned_data


class Step2Form(forms.Form):
    """Step 2: Credit preferences, max classes, and interests"""
    
    # Credit checkboxes
    credits_0 = forms.BooleanField(
        label='0 Credits',
        required=False,
        initial=True,
    )
    
    credits_1 = forms.BooleanField(
        label='1 Credit',
        required=False,
        initial=True,
    )
    
    credits_2 = forms.BooleanField(
        label='2 Credits',
        required=False,
        initial=True,
    )
    
    credits_4 = forms.BooleanField(
        label='4 Credits',
        required=False,
        initial=True,
    )
    
    # Maximum number of classes
    max_classes = forms.IntegerField(
        label="Maximum Number of Classes",
        min_value=1,
        max_value=7,
        initial=5,
        help_text="Between 1 and 7 classes",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., 5'
        })
    )
    
    # Interests description
    interests = forms.CharField(
        label="Tell us about your interests",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Describe your academic interests, career goals, or topics you\'re passionate about...',
            'rows': 6
        }),
        help_text="This helps us recommend courses that align with your interests"
    )
    
    def clean(self):
        """Ensure at least one credit option is selected"""
        cleaned_data = super().clean()
        
        # Check if at least one credit checkbox is selected
        credit_options = [
            cleaned_data.get('credits_0'),
            cleaned_data.get('credits_1'),
            cleaned_data.get('credits_2'),
            cleaned_data.get('credits_4'),
        ]
        
        if not any(credit_options):
            raise forms.ValidationError("Please select at least one credit option.")
        
        return cleaned_data
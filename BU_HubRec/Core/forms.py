from django import forms
from .models import Hub

class Step1Form(forms.Form):
    """Step 1: Hub Selection"""
    
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
    """Step 2: Preferences"""
    
    credits = forms.IntegerField(
        label="Number of Credits",
        min_value=1,
        max_value=20,
        initial=4,
        help_text="How many credits do you need?",
        widget=forms.NumberInput(attrs={
            'placeholder': 'e.g., 12'
        })
    )
    
    num_courses = forms.IntegerField(
        label="Number of Courses (Optional)",
        min_value=1,
        max_value=10,
        required=False,
        help_text="Leave blank for the minimum number of courses needed",
        widget=forms.NumberInput(attrs={
            'placeholder': 'Leave blank for minimum'
        })
    )
    
    only_next_semester = forms.BooleanField(
        label="Only Next Semester",
        required=False,
        initial=False,
        help_text="Only show courses offered next semester"
    )

class Step3Form(forms.Form):
    """Step 3: Interests Description"""
    
    interests = forms.CharField(
        label="Tell us about your interests",
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe your academic interests, career goals, or topics you\'re passionate about...',
            'rows': 6
        }),
        help_text="This helps us recommend courses that align with your interests"
    )
from django.shortcuts import render, redirect
import pprint

# Create your views here.

from django.shortcuts import render, get_object_or_404
from .models import Hub, Course, ClassData
import random

from formtools.wizard.views import SessionWizardView
from .forms import Step1Form, Step2Form, Step3Form

from .hub_optimizer import optimize_schedule

def index(request):
    # Get all ClassData IDs
    all_ids = list(ClassData.objects.values_list('id', flat=True))

    # Pick 40 random unique IDs (or fewer if not enough)
    random_ids = random.sample(all_ids, min(60, len(all_ids)))

    # Fetch the actual ClassData objects
    class_objects = ClassData.objects.filter(id__in=random_ids)

    # Build the list of class code strings using your __str__
    class_codes = [str(c) for c in class_objects]
    
    context = {
        'words': class_codes,
    }
    return render(request, 'Core\\index.html', context=context)

def pick_hub(request):
    hubs = Hub.objects.all().order_by("unit_name")
    return render(request, "Core\\pick_hub.html", {"hubs": hubs})

def display_hub_classes(request, hub_code):
    hub = get_object_or_404(Hub, unit_name=hub_code)
    courses = Course.objects.filter(hubs=hub).order_by("name")

    return render(request, "Core\\display_hub_classes.html", {
        "hub": hub,
        "courses": courses,
    })

def display_course_information(request, college, subject, catalog_number):
    class_data = get_object_or_404(
        ClassData,
        college=college,
        subject=subject,
        catalog_number=catalog_number,
    )

    course = get_object_or_404(Course, class_data=class_data)

    return render(request, "Core/display_course.html", {
        "course": course,
        "class_data": class_data,
    })



# Optimizer wizard view
class MyWizard(SessionWizardView):
    """Multi-step form wizard for course optimization"""
    
    template_name = "Core/optimizer_form.html"
    form_list = [Step1Form, Step2Form, Step3Form]

    def done(self, form_list, **kwargs):
        """
        Called when all forms are valid and submitted.
        Processes the data and renders the results.
        """
        # Combine all form data
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        
        # Debug: Print the raw data to console
        print("=" * 50)
        print("FORM DATA RECEIVED:")
        pprint.pprint({k: v for k, v in final_data.items() if 'hub' in k})
        print("=" * 50)
        
        # Process Step 1: Hub selections and counts
        selected_hubs = []
        for key, value in final_data.items():
            if key.startswith('hub_') and not key.endswith('_count'):
                if value:  # If the hub checkbox is checked
                    hub_code = key.replace('hub_', '')
                    count_key = f'{key}_count'
                    count_value = final_data.get(count_key)
                    
                    # Debug print for each hub
                    print(f"Processing {hub_code}: checkbox={value}, count_value={count_value}, type={type(count_value)}")
                    
                    # Handle None, empty string, or invalid counts
                    try:
                        count = int(count_value) if count_value is not None else 1
                        if count < 1:
                            count = 1
                    except (ValueError, TypeError):
                        count = 1
                    
                    print(f"  -> Final count for {hub_code}: {count}")
                    
                    # Get the Hub object
                    try:
                        hub = Hub.objects.get(unit_name=hub_code)
                        selected_hubs.append({
                            'hub': hub,
                            'code': hub_code,
                            'name': hub.get_unit_name_display(),
                            'count': count
                        })
                    except Hub.DoesNotExist:
                        print(f"  -> Hub {hub_code} not found!")
                        pass
        
        print(f"Selected hubs: {selected_hubs}")
        print("=" * 50)
        
        # Process Step 2: Preferences
        credits = final_data.get('credits')
        num_courses = final_data.get('num_courses')  # Can be None
        only_next_semester = final_data.get('only_next_semester', False)
        
        # Process Step 3: Interests
        interests = final_data.get('interests', '')
        
        # Build context for results page
        context = {
            'selected_hubs': selected_hubs,
            'total_hub_courses': sum(h['count'] for h in selected_hubs),
            'credits': credits,
            'num_courses': num_courses,
            'only_next_semester': only_next_semester,
            'interests': interests,
            'data': final_data,  # Original combined data for debugging
        }
        
        # 🛑 CRITICAL DEBUGGING SECTION 🛑
        optimized_schedule = []
        try:
            print("--- VIEWS.PY DEBUG: PRE-CALL TO OPTIMIZE_SCHEDULE ---")
            optimized_schedule = optimize_schedule(context)
            print("--- VIEWS.PY DEBUG: POST-CALL FROM OPTIMIZE_SCHEDULE ---")
        except Exception as e:
            # THIS MUST PRINT IF THERE IS A CRASH AT THE CALL SITE
            print(f"!!! VIEWS.PY CRITICAL ERROR: Failed to run optimize_schedule: {e}")
            
        context['schedule'] = optimized_schedule
        
        # Render the results page
        return render(self.request, "Core/optimizer_results.html", context)
    
    def get_form_initial(self, step):
        """
        Populate initial data for forms (useful for back button).
        """
        initial = self.initial_dict.get(step, {})
        return initial
    
    def get_context_data(self, form, **kwargs):
        """
        Add extra context to the template.
        """
        context = super().get_context_data(form=form, **kwargs)
        
        # Add step-specific context if needed
        if self.steps.current == '0':
            context['step_title'] = 'Select Hub Requirements'
        elif self.steps.current == '1':
            context['step_title'] = 'Set Your Preferences'
        elif self.steps.current == '2':
            context['step_title'] = 'Share Your Interests'
        
        return context
# Django imports
from django import forms
from datetime import date, timedelta

# Local Imports
from workshop_app.models import states, WorkshopType, Workshop

class FilterForm(forms.Form):
    from_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )
    to_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )
    workshop_type = forms.ModelChoiceField(
        queryset=WorkshopType.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    state = forms.ChoiceField(
        choices=states, required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    show_workshops = forms.BooleanField(
        help_text="Show my workshops only", required=False,
    )
    sort = forms.ChoiceField(
        choices=(("date", "Oldest"), ("-date", "Latest")),
        help_text="Sort by",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        start = kwargs.pop("start") if "start" in kwargs else None
        end = kwargs.pop("end") if "end" in kwargs else None
        selected_state = kwargs.pop("state") if "state" in kwargs else None
        selected_type = kwargs.pop("type") if "type" in kwargs else None
        show_workshops = (kwargs.pop("show_workshops")
                            if "show_workshops" in kwargs else None)
        sort = kwargs.pop("sort") if "sort" in kwargs else None
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["from_date"].initial = start
        self.fields["to_date"].initial = end
        self.fields["state"].initial = selected_state
        self.fields["workshop_type"].initial = selected_type
        self.fields["show_workshops"].initial = show_workshops
        self.fields["sort"].initial = sort


# ADD THIS NEW FORM FOR WORKSHOP PROPOSAL
class WorkshopProposalForm(forms.ModelForm):
    workshop_type = forms.ModelChoiceField(
        queryset=WorkshopType.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'id': 'id_workshop_type'
            }
        ),
        help_text="Select the workshop type you want to propose"
    )
    
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control datepicker',
                'id': 'id_date',
                'placeholder': 'Select workshop date'
            }
        ),
        help_text="Select your preferred workshop date"
    )
    
    tnc_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                'id': 'id_tnc_accepted'
            }
        ),
        help_text="You must accept the terms and conditions"
    )
    
    class Meta:
        model = Workshop  # Replace with your actual Workshop model
        fields = ['workshop_type', 'date', 'tnc_accepted']
    
    def __init__(self, *args, **kwargs):
        super(WorkshopProposalForm, self).__init__(*args, **kwargs)
        
        # Set date restrictions
        today = date.today()
        min_date = today + timedelta(days=3)  # 3 days from today
        max_date = today + timedelta(days=365)  # 1 year from today
        
        self.fields['date'].widget.attrs.update({
            'min': min_date.strftime('%Y-%m-%d'),
            'max': max_date.strftime('%Y-%m-%d')
        })
    
    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date:
            today = date.today()
            min_date = today + timedelta(days=3)
            max_date = today + timedelta(days=365)
            
            if selected_date < min_date:
                raise forms.ValidationError("Workshop date must be at least 3 days from today.")
            
            if selected_date > max_date:
                raise forms.ValidationError("Workshop date cannot be more than 1 year from today.")
            
            # Check if selected date is a weekend
            if selected_date.weekday() in [5, 6]:  # 5=Saturday, 6=Sunday
                raise forms.ValidationError("Workshop cannot be scheduled on weekends.")
        
        return selected_date

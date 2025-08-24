# providers/forms.py
from django import forms
from .models import ServiceProvider, ProviderService, ServiceLocation, WorkingHours, BlockedSlot, ProviderTimeSlot
from services.models import ServiceCategory, ServiceSubCategory, Service

class ProviderServiceForm(forms.ModelForm):
    # These fields are defined for dynamic behavior.
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        label="Service Category",
        required=True
    )
    sub_category = forms.ModelChoiceField(
        queryset=ServiceSubCategory.objects.none(),
        label="Service Sub-category",
        required=True
    )

    class Meta:
        model = ProviderService
        fields = ['category', 'sub_category', 'name', 'description', 'duration_minutes', 'price', 'image', 'locations']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'locations': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If the form is being initialized with an existing instance (for editing),
        # set the initial values.
        if self.instance and self.instance.pk:
            self.fields['category'].initial = self.instance.sub_category.category
            self.fields['sub_category'].initial = self.instance.sub_category
            
            # Populate the sub_category queryset based on the instance's category
            self.fields['sub_category'].queryset = ServiceSubCategory.objects.filter(
                category=self.instance.sub_category.category
            ).order_by('name')
        # This handles the AJAX request when the category is changed
        elif 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = ServiceSubCategory.objects.filter(
                    category_id=category_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        
        # Fallback: if no instance or no category is selected, show all subcategories.
        # This also applies to the initial load of the "add new service" form.
        else:
            self.fields['sub_category'].queryset = ServiceSubCategory.objects.all().order_by('name')
        # Ensure locations queryset is always set
        self.fields['locations'].queryset = ServiceLocation.objects.all()



class ProviderTimeSlotForm(forms.ModelForm):
    class Meta:
        model = ProviderTimeSlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class ProviderBlockedSlotForm(forms.ModelForm):
    class Meta:
        model = BlockedSlot
        fields = ['date', 'start_time', 'end_time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class WorkingHoursForm(forms.ModelForm):
    class Meta:
        model = WorkingHours
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class ProviderServiceEditForm(forms.ModelForm):
    class Meta:
        model = ProviderService
        fields = ['name', 'description', 'duration_minutes', 'price', 'image', 'locations']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'locations': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['locations'].queryset = ServiceLocation.objects.all()
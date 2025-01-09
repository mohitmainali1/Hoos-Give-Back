from django import forms
from .models import *
from .models import Project, Document

# Widget for time selection dropdown menu
class TimeDropdown(forms.Select):
    def __init__(self, *args, **kwargs):
        time_choices = []
        for hour in range(24):
            for minute in (0, 30):
                hour_12 = hour % 12 or 12
                if hour < 12:
                    period = "AM"
                else:
                    period = "PM"
                formatted_time = f"{hour_12}:{minute:02} {period}"
                value_time = f"{hour:02}:{minute:02}"
                time_choices.append((value_time, formatted_time))

        kwargs['choices'] = time_choices
        super().__init__(*args, **kwargs)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'collaborators', 'project_date', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'collaborators': forms.CheckboxSelectMultiple(),
            'project_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': TimeDropdown(),
            'end_time': TimeDropdown(),
        }

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ApproveRequestsForm(forms.Form):
    requests = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Approve User Requests"
    )

    def __init__(self, *args, **kwargs):
        pending_requests = kwargs.pop('pending_requests', None)
        super().__init__(*args, **kwargs)
        if pending_requests is not None:
            self.fields['requests'].queryset = pending_requests

class AddCollaboratorsForm(forms.Form):
    collaborators = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
        label="Select Collaborators"
    )

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'keywords']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Document Title',
            'file': 'File',
            'keywords': 'Keywords (comma-separated)',
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "is_completed"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "is_completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
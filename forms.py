from django import forms
from .models import PackingListJob


class DATFileUploadForm(forms.ModelForm):
    """Form for uploading DAT files"""
    
    class Meta:
        model = PackingListJob
        fields = ['dat_file']
        widgets = {
            'dat_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.dat',
                'id': 'datFileInput'
            })
        }
        labels = {
            'dat_file': 'Select DAT File'
        }
    
    def clean_dat_file(self):
        """Validate uploaded file"""
        dat_file = self.cleaned_data.get('dat_file')
        
        if dat_file:
            # Check file extension
            if not dat_file.name.endswith('.dat'):
                raise forms.ValidationError('Only .dat files are allowed.')
            
            # Check file size (max 10MB)
            if dat_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 10MB.')
        
        return dat_file
from django import forms


class BuildPDFsForm(forms.Form):
    """Prompt the user for the number of PDFs to build"""
    num_pdfs = forms.CharField(
        label="PDFs to produce",
        widget=forms.NumberInput(attrs={'min': 1, 'max': 10000})
    )
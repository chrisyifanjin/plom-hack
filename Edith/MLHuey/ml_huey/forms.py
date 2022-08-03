from cProfile import label
from tkinter import Widget
from django import forms


class AddTwoNumbersForm(forms.Form):
    first = forms.CharField(
        max_length=150,
        label="First number",
        widget=forms.NumberInput(attrs={'min': 0})
    )
    second = forms.CharField(
        max_length=150,
        label="Second number",
        widget=forms.NumberInput(attrs={'min': 0})
    )


class NumberGuessForm(forms.Form):
    is_even_guess = forms.BooleanField(
        label="Will it be even?",
        required=False,
        widget=forms.CheckboxInput()
    )

from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'size', 'color', 'cost_price', 'selling_price', 'quantity', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SKU / Barcode'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter color (optional)'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # If the user is NOT a superuser (i.e. regular user), they cannot edit the cost price.
        if user and not user.is_superuser:
            self.fields['cost_price'].required = False
            self.fields['cost_price'].widget = forms.HiddenInput()
            if self.instance and self.instance.pk:
                self.fields['cost_price'].initial = self.instance.cost_price
            else:
                self.fields['cost_price'].initial = 0.00

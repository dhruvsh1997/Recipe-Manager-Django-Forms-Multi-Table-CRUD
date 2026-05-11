from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'cuisine', 'prep_minutes', 'instructions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'inp'}),
            'cuisine': forms.TextInput(attrs={'class': 'inp'}),
            'prep_minutes': forms.NumberInput(attrs={'class': 'inp'}),
            'instructions': forms.Textarea(attrs={'class': 'inp', 'rows': 5}),
        }

    def clean_prep_minutes(self):
        # Field-level custom validation
        value = self.cleaned_data['prep_minutes']
        if value > 600:
            raise forms.ValidationError("Prep time can't exceed 10 hours.")
        return value


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'inp'}),
            'quantity': forms.TextInput(attrs={'class': 'inp'}),
        }


# This is the multi-table magic.
# A formset = multiple forms of the same kind grouped together.
# inlineformset_factory ties Ingredient forms to a parent Recipe automatically.
IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient,
    form=IngredientForm,
    extra=2,             # 2 blank ingredient rows on a fresh page
    can_delete=True,     # render checkboxes to remove existing rows
)


class RecipeSearchForm(forms.Form):
    """Plain Form (not ModelForm) since search isn't tied to one model."""
    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'inp', 'placeholder': 'Search recipes…'}))
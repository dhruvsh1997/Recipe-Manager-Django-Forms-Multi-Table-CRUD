from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.db import transaction
from .models import Recipe
from .forms import RecipeForm, IngredientFormSet, RecipeSearchForm


def recipe_list(request):
    search = RecipeSearchForm(request.GET or None)
    recipes = Recipe.objects.all().prefetch_related('ingredients')
    if search.is_valid() and search.cleaned_data['q']:
        q = search.cleaned_data['q']
        recipes = recipes.filter(Q(name__icontains=q) | Q(cuisine__icontains=q))
    return render(request, 'kitchen/recipe_list.html',
                  {'recipes': recipes, 'search': search})


def recipe_add(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        formset = IngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():           # all-or-nothing save
                recipe = form.save()
                formset.instance = recipe        # link children to parent
                formset.save()
            return redirect('kitchen:recipe_list')
    else:
        form = RecipeForm()
        formset = IngredientFormSet()
    return render(request, 'kitchen/recipe_form.html',
                  {'form': form, 'formset': formset, 'action': 'Add'})


def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        formset = IngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('kitchen:recipe_list')
    else:
        form = RecipeForm(instance=recipe)
        formset = IngredientFormSet(instance=recipe)
    return render(request, 'kitchen/recipe_form.html',
                  {'form': form, 'formset': formset, 'action': 'Edit'})


def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()                          # soft delete
        return redirect('kitchen:recipe_list')
    return render(request, 'kitchen/recipe_confirm_delete.html', {'recipe': recipe})


def trash_list(request):
    cutoff = timezone.now() - timedelta(days=1)
    deleted = Recipe.all_objects.filter(is_deleted=True, deleted_at__gte=cutoff)
    return render(request, 'kitchen/trash_list.html', {'recipes': deleted})


def recipe_restore(request, pk):
    recipe = get_object_or_404(Recipe.all_objects, pk=pk, is_deleted=True)
    if recipe.is_recoverable:
        recipe.restore()
    return redirect('kitchen:trash_list')


def recipe_hard_delete(request, pk):
    recipe = get_object_or_404(Recipe.all_objects, pk=pk)
    if request.method == 'POST':
        recipe.delete(hard=True)
        return redirect('kitchen:trash_list')
    return render(request, 'kitchen/recipe_confirm_hard_delete.html',
                  {'recipe': recipe})
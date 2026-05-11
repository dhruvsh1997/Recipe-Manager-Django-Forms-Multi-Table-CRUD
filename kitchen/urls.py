from django.urls import path
from . import views

app_name = 'kitchen'
urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('add/', views.recipe_add, name='recipe_add'),
    path('<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('trash/', views.trash_list, name='trash_list'),
    path('<int:pk>/restore/', views.recipe_restore, name='recipe_restore'),
    path('<int:pk>/hard-delete/', views.recipe_hard_delete, name='recipe_hard_delete'),
]
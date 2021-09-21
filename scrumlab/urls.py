"""scrumlab URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from jedzonko import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index_view),
    path('clear_likes/', views.clear_likes, name='clear_likes'),
    #Landing page
    path('', views.start_view),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    #App main
    path('main/', views.dashboard),
    path('recipe/<int:recipe_id>/', views.recipe_details, name='recipe_details'),
    path('recipe/list/', views.recipe_list, name='recipe_list'),
    path('recipe/add/', views.recipe_add, name='recipe_add'),
    path('recipe/modify/<int:recipe_id>/', views.recipe_edit, name='recipe_edit'),
    path('recipe/delete/<int:recipe_id>/', views.recipe_delete, name='recipe_delete'),
    path('plan/<int:plan_id>/', views.plan_details, name='plan_details'),
    path('plan/list/', views.plan_list, name='plan_list'),
    path('plan/add/', views.plan_add, name='plan_add'),
    path('plan/delete/<int:plan_id>/', views.plan_delete, name='plan_delete'),
    path('plan/add-recipe/', views.plan_add_recipe, name='plan_add_recipe'),
    path("plan/modify/<int:plan_id>/", views.plan_edit, name="plan_edit"),
    path('plan/remove-recipe/<int:recipeplan_id>/', views.plan_remove_recipe, name='plan_remove_recipe'),

]

from datetime import datetime
from random import shuffle

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from jedzonko.models import Recipe, Plan, RecipePlan, DayName, Page
from jedzonko import utils


def index_view(request):
    ctx = {"actual_date": datetime.now()}
    return render(request, "test.html", ctx)


def start_view(request):
    # carousel
    recipes = list(Recipe.objects.all())
    shuffle(recipes)

    # contact and about
    page_contact = ''
    page_about = ''
    try:
        page_contact = Page.objects.get(slug='contact')
        page_about = Page.objects.get(slug='about')
    except ObjectDoesNotExist:
        pass
    back = utils.get_current_page_back_url(request)
    return render(request, 'index.html', {'recipes': recipes[:3], 'page_contact': page_contact,
                                          'page_about': page_about, 'back': back})


def contact(request):
    # Przykladowy contact do stworzenia
    # Page.objects.create(title='Szybki Kontakt',description='Email: Jedzonko@jedonko.pl\nTelefon: 38 273 22 31\npn.-pt.: 8:30 - 18:00\nsob.: 9:00 - 14:00\nUl. Żarcia 53\n12-321 Mnóstwo', slug='contact')
    page_contact = Page.objects.get(slug='contact')
    description_lst = page_contact.description.split("\n")
    return render(request, "contact.html", {'page_contact': page_contact, 'description_lst': description_lst})


def about(request):
    # Przykladowy about do stworzenia
    # Page.objects.create(title='Zaplanuj jedzonko', description='Innowacjna aplikacja do tworzenia planów żywieniowych, autorstwa Marii Iksińskiej. Aplikacja kierowana jest do wszystkich osób chcących zacząć jeść zdrowo i zmienić swoje życie na lepsze! Dzieki naszej aplikacjiplanowanie posiłków oraz całych planów żywieniowych będzie proste, przyjemne, a przede wzystkim pełne smaku!!', slug='about')
    page_about = Page.objects.get(slug='about')
    return render(request, "about.html", {'page_about': page_about})


def recipe_details(request, recipe_id):
    if "liked" not in request.session:
        request.session["liked"] = ""
    if "disliked" not in request.session:
        request.session["disliked"] = ""
    if str(recipe_id) in request.session.get("liked", "").split(","):
        like_it_text = "lubisz to :)"
        dislike_it_text = "nie lub"
        like_status = f"<span style='color: #1e7e34'> lubisz</span>"
    elif str(recipe_id) in request.session.get("disliked", "").split(","):
        like_it_text = "polub przepis"
        dislike_it_text = "nie lubisz :("
        like_status = f"<span style='color: crimson'> nie lubisz</span>"
    else:
        like_it_text = "polub przepis"
        dislike_it_text = "nie lub"
        like_status = ""

    if request.method == "GET":
        recipe = Recipe.objects.get(id=recipe_id)
        ingredients = recipe.ingredients
        ingredients = ingredients.split('\n')
        # dynamiczny powrót
        back = request.GET.get('back', '')

        return render(request, 'app-recipe-details.html', {'recipe': recipe, 'ingredients': ingredients,
                                                           'like_it_text': like_it_text, 'like_status': like_status,
                                                           'dislike_it_text': dislike_it_text, 'back': back})
    else:
        liked_list = request.session.get("liked", "").split(",")
        disliked_list = request.session.get("disliked", "").split(",")
        # dynamiczny powrót
        back = request.POST.get('back', '')

        if request.POST.get("submit") == "like":  # weszliśmy przyciskiem LIKE
            if str(recipe_id) in liked_list:  # jest już lajk, więc go zdejmujemy
                votes = -1
                liked_list.remove(str(recipe_id))
            else:  # nie ma lajka, więc dajemy
                liked_list.append(str(recipe_id))
                if str(recipe_id) in disliked_list:  # jeżeli był dislajk
                    votes = 2
                    disliked_list.remove(str(recipe_id))
                else:  # nie było dislajka
                    votes = 1
        else:  # weszliśmy przyciskiem DISLIKE
            if str(recipe_id) in disliked_list:  # jest już dislajk, więc go zdejmujemy
                votes = 1
                disliked_list.remove(str(recipe_id))
            else:  # nie ma dislajka, więc dajemy
                disliked_list.append(str(recipe_id))
                if str(recipe_id) in liked_list:  # jeżeli był lajk
                    votes = -2
                    liked_list.remove(str(recipe_id))
                else:  # nie było lajka
                    votes = -1

        recipe = Recipe.objects.get(pk=recipe_id)
        recipe.votes += votes
        recipe.save()
        request.session["liked"] = ",".join(liked_list)
        request.session["disliked"] = ",".join(disliked_list)
        str1 = f"{recipe.get_url()}{utils.get_back_url(back)}"
        return redirect(f"{recipe.get_url()}{utils.get_back_url(back)}")


def recipe_list(request):
    search_term = request.GET.get('search_term', '')
    if search_term == '':
        recipes = Recipe.objects.all().order_by('-votes', '-created')
    else:
        recipes = Recipe.objects.filter(name__icontains=search_term).order_by('-votes', '-created')

    paginator = Paginator(recipes, 3)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    back = utils.get_current_page_back_url(request)  # dla dynamicznych powrotów
    return render(request, 'app-recipes.html', {"recipes": page_obj, "search_term": search_term, "back": back})


def recipe_add(request):
    return recipe_edit(request)


def recipe_edit(request, recipe_id=None):
    if request.method == "GET":
        back = request.GET.get('back', '/recipe/list/')
        if recipe_id:
            # pojawia się formatka do poprawienia istniejacego rekordu
            recipe = Recipe.objects.get(pk=recipe_id)
            return render(request, "app-edit-recipe.html",
                          {"name": recipe.name, "prep_time": recipe.preparation_time, "description": recipe.description,
                           "ingredients": recipe.ingredients, "prep_details": recipe.preparation_details,
                           "back": back})
        else:
            # pojawia się pusta formatka, tworząca nowy rekord
            return render(request, 'app-add-recipe.html', {"prep_time": 0, "back": back})
    else:
        # ta część jest aktywna, gdy zatwierdzimy formularz dodawania/edycji
        back = request.POST.get('back', '')
        name = request.POST.get("recipe-name")
        prep_time = int(request.POST.get("recipe-time"))
        description = request.POST.get("recipe-description")
        prep_details = request.POST.get("recipe-prep-det")
        ingredients = request.POST.get("recipe-ingredients")
        # jeżeli poprawnie wypełnione pola
        if name and description and ingredients and prep_details:
            if recipe_id and request.POST.get("submit") == "update":
                # zapisujemy poprawiony istniejący rekord
                recipe = Recipe.objects.get(pk=recipe_id)
                recipe.name = name
                recipe.preparation_time = prep_time
                recipe.description = description
                recipe.ingredients = ingredients
                recipe.preparation_details = prep_details
                recipe.save()
            else:
                pass
                # zapisujemy nowy rekord do bazy danych
                Recipe.objects.create(name=name, preparation_time=prep_time, description=description,
                                      ingredients=ingredients, preparation_details=prep_details)
            # po zapisaniu wracamy na widok listy przepisów
            str1 = back
            return redirect(back)
        # jeżeli któreś pole nie zostało wypełnione
        else:
            if recipe_id:
                str1 = back
                str2 = utils.get_back_url(back)
                # ekran edycji istniejącego przepisu z komunikatem o niewypełnionych polach
                return render(request, "app-edit-recipe.html", {"name": name, "prep_time": prep_time,
                                                                "description": description, "ingredients": ingredients,
                                                                "prep_details": prep_details,
                                                                "back": back,
                                                                "message": "Wszystkie pola muszą być wypełnione!"})

            else:
                # ekran dodawania przepisu z komunikatem o niewypełnionych polach
                return render(request, "app-add-recipe.html", {"name": name, "prep_time": prep_time,
                                                               "description": description, "ingredients": ingredients,
                                                               "prep_details": prep_details,
                                                               "back": back,
                                                               "message": "Wszystkie pola muszą być wypełnione!"})


def recipe_delete(request, recipe_id):
    if request.method == "GET":
        back = request.GET.get('back', '')
        data_description = "przepis"
        query_details = "Spowoduje to zdjęcie przepisu z wszystkich planów oraz trwałe usunięcie z bazy danych."
        return render(request, "delete_query_form.html", {'data_description': data_description,
                                                          'query_details': query_details, 'back': back})
    else:
        back = request.POST.get('back', '')
        if request.POST.get('submit') == 'accept':
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.delete()
        return redirect(back)


def dashboard(request):
    plan_count = len(list(Plan.objects.all()))
    recipe_count = len(list(Recipe.objects.all()))
    latest_plan = list(Plan.objects.all().order_by('-created'))[0]
    recipes = latest_plan.recipeplan_set.all()

    recipes_lst = []

    for i in range(1, 8):
        tmp = recipes.filter(day_name=i)
        if tmp:
            recipes_lst.append(tmp.order_by('order'))
    back = utils.get_current_page_back_url(request)  # dynamiczny powrót
    return render(request, "dashboard.html", {'plan_count': plan_count, 'recipe_count': recipe_count,
                                              'plan': latest_plan, 'recipes_lst': recipes_lst, 'back': back})


def plan_details(request, plan_id):
    plan = Plan.objects.get(id=plan_id)
    back_details = utils.get_current_page_back_url(request)  # dla dynamicznych powrotów do tej strony
    back = request.GET.get('back', '')  # dokąd wracać z tej strony
    return render(request, 'app-details-schedules.html', {'plan': plan, 'back': back, 'back_details': back_details})


def plan_list(request):
    list_of_plans = list(Plan.objects.all().order_by('name'))
    paginator = Paginator(list_of_plans, 3)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    back = utils.get_current_page_back_url(request)  # dla dynamicznych powrotów
    return render(request, "app-schedules.html", {'page_obj': page_obj, 'back': back})


def plan_add(request):
    if request.method == "GET":
        return render(request, 'app-add-schedules.html')
    else:
        name = request.POST['name']
        description = request.POST['description']
        if len(name) > 0 and len(description) > 0:
            p = Plan.objects.create(name=name, description=description)
        else:
            return render(request, 'app-add-schedules.html',
                          {'message': 'Błąd! Pola nie mogą być puste. Spróbuj jeszcze raz'})
    return redirect(f'/plan/{p.id}/')


def plan_edit(request, plan_id):
    if request.method == 'GET':
        plan = Plan.objects.get(pk=plan_id)
        return render(request, 'app-edit-schedules.html', {'plan': plan})
    else:
        name = request.POST.get('name')
        description = request.POST.get('description')
        plan = Plan.objects.get(pk=plan_id)
        plan.name = name
        plan.description = description
        plan.save()
        return redirect('/plan/list')


def plan_add_recipe(request):
    if request.method == 'GET':
        back = request.GET.get('back', '')
        return render(request, 'app-schedules-meal-recipe.html',
                      {'plans': list(Plan.objects.all().order_by('name')),
                       'recipes': list(Recipe.objects.all()),
                       'days': list(DayName.objects.all()),
                       'back': back})
    else:
        id_plan = int(request.POST['plan'])
        plan = Plan.objects.get(pk=id_plan)
        meal_name = request.POST['meal_name']
        meal_num = request.POST['meal_num']
        id_recipe = int(request.POST['recipe'])
        recipe = Recipe.objects.get(pk=id_recipe)
        id_day = int(request.POST['day'])
        day = DayName.objects.get(pk=id_day)
        back = request.POST.get('back', '')
        if back == '':
            back = f'/plan/{id_plan}'

    RecipePlan.objects.create(
        plan=plan, meal_name=meal_name, order=meal_num, recipe=recipe, day_name=day)
    return redirect(back)


def plan_remove_recipe(request, recipeplan_id):
    RecipePlan.objects.get(pk=recipeplan_id).delete()
    return redirect(request.META.get('HTTP_REFERER'))


def plan_delete(request, plan_id):
    if request.method == "GET":
        back = request.GET.get('back', '')
        data_description = "plan"
        query_details = "Spowoduje to trwałe usunięcie planu z bazy danych."
        return render(request, "delete_query_form.html", {'data_description': data_description,
                                                          'query_details': query_details, 'back': back})
    else:
        back = request.POST.get('back', '')
        if request.POST.get('submit') == 'accept':
            plan = Plan.objects.get(pk=plan_id)
            plan.delete()
        return redirect(back)


# tego można użyć, żeby wyczyścić lajki przy przepisach
def clear_likes(request):
    if "liked" in request.session:
        del request.session["liked"]
    if "disliked" in request.session:
        del request.session["disliked"]
    return HttpResponse("wyczyszczono z sesji dane polubień/znielubień")

from django.db import models
# from jedzonko.enums import Dayname


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    ingredients = models.TextField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    preparation_time = models.IntegerField()
    votes = models.IntegerField(default=0)
    preparation_details = models.TextField(default="")

    def __str__(self):
        return self.name

    def get_short_desc(self):
        if len(self.description) > 200:
            return f"{self.description[0:200] + '...'}"
        else:
            return self.description

    def get_url(self):
        return f"/recipe/{self.id}/"


class Plan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    plan_recipes = models.ManyToManyField(Recipe, through='RecipePlan')

    def get_meals_for_week(self):
        days = DayName.objects.order_by('order')
        recipes_for_week = []
        for day in days:
            krotka = (day.day_name, RecipePlan.objects.filter(plan=self, day_name=day).order_by('order'))
            recipes_for_week.append(krotka)
        return recipes_for_week

    def __str__(self):
        return self.name

    def get_url(self):
        return f"/plan/{self.id}"


class RecipePlan(models.Model):
    meal_name = models.CharField(max_length=255)
    order = models.IntegerField()
    day_name = models.ForeignKey('DayName', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.meal_name


class Page(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class DayName(models.Model):
    day_name = models.CharField(max_length=16)
    order = models.IntegerField(unique=True)
    
    def __repr__(self):
        return self.id


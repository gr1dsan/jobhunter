import json
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class SoftSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class HardSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Seeker(models.Model):
    title = models.CharField(max_length=255)
    keyword = models.CharField(max_length=255, blank=True)
    cities = models.TextField(blank=True, default="[]")
    categories = models.TextField(blank=True, default="[]")
    working_hours = models.TextField(blank=True, default="[]")
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_cities(self):
        return json.loads(self.cities) if self.cities else []

    def get_categories(self):
        return json.loads(self.categories) if self.categories else []

    def get_working_hours(self):
        return json.loads(self.working_hours) if self.working_hours else []

    def set_cities(self, value):
        self.cities = json.dumps(value)

    def set_categories(self, value):
        self.categories = json.dumps(value)

    def set_working_hours(self, value):
        self.working_hours = json.dumps(value)


class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    locations = models.ManyToManyField(Location, blank=True)
    details = models.TextField(blank=True, default="")
    url = models.URLField(max_length=500, blank=True, default="")
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_net = models.BooleanField(default=False)
    is_gross = models.BooleanField(default=False)
    is_full_time = models.BooleanField(default=False)
    is_part_time = models.BooleanField(default=False)
    soft_skills = models.ManyToManyField(SoftSkill, blank=True)
    hard_skills = models.ManyToManyField(HardSkill, blank=True)
    seeker = models.ForeignKey(Seeker, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"
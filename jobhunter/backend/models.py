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

    def __str__(self):
        return f"{self.title} at {self.company}"
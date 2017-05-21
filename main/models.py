from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

class Url(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return str(self.url)

class User(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=15)

    def __str__(self):
        return str(self.email) + " [" + str(self.name) + " " + str(self.surname) + "]"

class SavedUrl(models.Model):
    user = models.ForeignKey(User)
    url = models.ForeignKey(Url, blank=True, null=True)
    category = models.ForeignKey(Category)

    url_title = models.CharField(max_length=150, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)

    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "[" + str(self.user) + "] " + str(self.url) + " Category: " + str(self.category)

    class Meta:
        unique_together = (("user", "url"),)

class Label(models.Model):
    saved_url = models.ManyToManyField(SavedUrl)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)

# asi tu nebude...
class Citation(models.Model):
    saved_url = models.ForeignKey(SavedUrl)
    text = models.CharField(max_length=5000, unique=True)

    def __str__(self):
        return str(self.text[:50])




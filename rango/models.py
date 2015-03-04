from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify



class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        # Create the slug only once to avoid broken links if name is changed
        if not self.id:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __unicode__(self):
        return self.user.username

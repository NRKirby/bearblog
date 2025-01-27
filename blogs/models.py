from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from taggit.managers import TaggableManager
from math import log


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    title = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    subdomain = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(max_length=128, blank=True, null=True)

    nav = models.CharField(max_length=500, default="[Home](/)\n[Blog](/blog/)", blank=True)
    content = models.TextField(default="Hello World!", blank=True)
    meta_description = models.CharField(max_length=200, blank=True)
    meta_image = models.CharField(max_length=200, blank=True)
    lang = models.CharField(max_length=10, default='en', blank=True)
    meta_tag = models.CharField(max_length=500, blank=True, help_text="Custom meta tag")

    reviewed = models.BooleanField(default=False)
    upgraded = models.BooleanField(default=False)
    upgraded_date = models.DateTimeField(blank=True, null=True)
    blocked = models.BooleanField(default=False)

    external_stylesheet = models.CharField(max_length=255, blank=True)
    custom_styles = models.TextField(blank=True)
    overwrite_styles = models.BooleanField(
        default=False,
        choices=((True, 'Overwrite styles'), (False, 'Extend existing styles')),
        verbose_name='')
    favicon = models.CharField(max_length=4, default="🐼")

    fathom_site_id = models.CharField(max_length=8, blank=True)

    @property
    def contains_code(self):
        return "```" in self.content

    def bear_domain(self):
        return f'http://{self.subdomain}.{Site.objects.get_current().domain}'

    def useful_domain(self):
        if self.domain:
            return f'http://{self.domain}'
        else:
            return f'http://{self.subdomain}.{Site.objects.get_current().domain}'

    def __str__(self):
        return f'{self.title} ({self.useful_domain()})'


class Post(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    published_date = models.DateTimeField(blank=True)
    tags = TaggableManager(blank=True)
    publish = models.BooleanField(default=True)
    show_in_feed = models.BooleanField(default=True)
    is_page = models.BooleanField(default=False)
    content = models.TextField()
    canonical_url = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=200, blank=True)
    meta_image = models.CharField(max_length=200, blank=True)

    upvotes = models.IntegerField(default=0)
    score = models.FloatField(default=0)

    @property
    def contains_code(self):
        return "```" in self.content

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self.slug.lower()
        super(Post, self).save(*args, **kwargs)

    def update_score(self):

        self.upvotes = len(self.upvote_set.all())

        if self.upvotes > 1:
            log_of_upvotes = log(self.upvotes, 10)

            seconds = self.published_date.timestamp()
            if seconds > 0:
                score = (log_of_upvotes) + ((seconds - 1577811600) / (14 * 86400))
                self.score = score

                self.save()
        return


class Upvote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.created_date.strftime('%d %b %Y, %X')} - {self.ip_address} - {self.post}"


class Hit(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.created_date.strftime('%d %b %Y, %X')} - {self.ip_address} - {self.post}"


class Subscriber(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    email_address = models.EmailField()
    subscribed_date = models.DateTimeField(auto_now_add=True)

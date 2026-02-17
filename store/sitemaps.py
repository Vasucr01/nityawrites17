from django.contrib.sitemaps import Sitemap
from .models import Book
from django.urls import reverse

class BookSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Book.objects.filter(stock__gt=0)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('book_detail', args=[obj.pk])

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)

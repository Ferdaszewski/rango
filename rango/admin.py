from django.contrib import admin
from rango.models import Category, Page, UserProfile


admin.AdminSite.site_header = "Rango Administration"

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'category')
    list_filter = ['category']
    search_fields = ['title']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'views', 'likes')
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

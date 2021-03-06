from django.contrib import admin
from rango.models import Category, Page
from rango.models import UserProfile

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

class pageAdmin(admin.ModelAdmin):
        list_display = ('title','category','url')
        list_filter = ['category']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, pageAdmin)
admin.site.register(UserProfile)

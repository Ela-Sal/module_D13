from django.contrib import admin
from .models import Post, Category, Response, Reply


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Response)
admin.site.register(Reply)
# Register your models here.

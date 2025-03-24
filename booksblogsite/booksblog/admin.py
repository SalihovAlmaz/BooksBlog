from django.contrib import admin

from .models import Book, Genres, ReadingStatus, Review, Tags


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ['title', 'author', 'description','photo', 'slug', 'genres', 'tags']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(ReadingStatus)

admin.site.register(Review)






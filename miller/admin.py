from django.contrib import admin

# Register your models here.

from .models import Story, Tag, Document, Caption, Mention, Author

admin.site.register(Story)
admin.site.register(Tag)
admin.site.register(Document)
admin.site.register(Caption)
admin.site.register(Mention)
admin.site.register(Author)

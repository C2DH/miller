#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from codemirror import CodeMirrorTextarea

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from miller.models import Profile, Story, Tag, Document, Caption, Mention, Author, Comment, Review

codemirror_json_widget = CodeMirrorTextarea(mode="css", theme="elegant", config={ 
  'fixedGutter': True, 
  'lineNumbers':True, 
  'matchBrackets': True,
  'autoCloseBrackets': True,
  'lineWrapping': True
})

class BlogTagsListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('type of blogpost')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'type-of-blogpost'

    def lookups(self, request, model_admin):
        
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return Tag.objects.filter(category=Tag.BLOG).values_list('slug', 'name')
        

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is None:
          return queryset
        return queryset.filter(tags__category=Tag.BLOG, tags__slug=self.value())

class WritingTagsListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('type of writing')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'type-of-writing'

    def lookups(self, request, model_admin):
        
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return Tag.objects.filter(category=Tag.WRITING).values_list('slug', 'name')
        

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is None:
          return queryset
        return queryset.filter(tags__category=Tag.WRITING, tags__slug=self.value())

# Define an inline admin descriptor for Profile model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'profiles'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
  inlines = (ProfileInline, )



class AuthorAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(AuthorAdminForm, self).__init__(*args, **kwargs)
    self.fields['metadata'].widget = codemirror_json_widget

  def clean_metadata(self):
    try:
      metadata = json.loads(self.cleaned_data['metadata'])
    except ValueError as e:
      raise forms.ValidationError(u'%s'%e)
      # Expecting property name enclosed in double quotes: line 14 column 5 (char 1275)
    
    return self.cleaned_data['metadata']


class AuthorAdmin(admin.ModelAdmin):
  search_fields = ['fullname', 'metadata']
  form = AuthorAdminForm



class DocumentAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(DocumentAdminForm, self).__init__(*args, **kwargs)
    self.fields['contents'].widget = codemirror_json_widget

  def clean_contents(self):
    try:
      contents = json.loads(self.cleaned_data['contents'])
    except ValueError as e:
      raise forms.ValidationError(u'%s'%e)
      # Expecting property name enclosed in double quotes: line 14 column 5 (char 1275)
    
    return self.cleaned_data['contents']

class DocumentAdmin(admin.ModelAdmin):
  search_fields = ['title', 'contents', 'url', 'slug']
  exclude=['copyright']
  list_filter = ('type',)
  form = DocumentAdminForm

class CaptionAdmin(admin.ModelAdmin):
  search_fields = ['contents']



class CaptionInline(admin.TabularInline):
  model = Caption
  extra = 2 # how many rows to show


class StoryAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    codemirror_md_widget = CodeMirrorTextarea(mode="markdown", theme="elegant", config={ 
      'fixedGutter': True, 
      'lineNumbers':True, 
      'matchBrackets': True,
      'autoCloseBrackets': True,
      'lineWrapping': True
    })

    

    super(StoryAdminForm, self).__init__(*args, **kwargs)
    self.fields['contents'].widget = codemirror_md_widget
    self.fields['metadata'].widget = codemirror_json_widget


  def clean_metadata(self):
    try:
      metadata = json.loads(self.cleaned_data['metadata'])
    except ValueError as e:
      raise forms.ValidationError(u'%s'%e)
      # Expecting property name enclosed in double quotes: line 14 column 5 (char 1275)
    
    return self.cleaned_data['metadata']

class StoryAdmin(admin.ModelAdmin):
  # inlines = (CaptionInline,)
  exclude=['cover', 'cover_copyright', 'watchers', 'stories']
  search_fields = ['title']
  list_filter = ('status', WritingTagsListFilter, BlogTagsListFilter)
  form = StoryAdminForm


class TagAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(TagAdminForm, self).__init__(*args, **kwargs)
    self.fields['metadata'].widget = codemirror_json_widget

  def clean_contents(self):
    try:
      contents = json.loads(self.cleaned_data['metadata'])
    except ValueError as e:
      raise forms.ValidationError(u'%s'%e)
      # Expecting property name enclosed in double quotes: line 14 column 5 (char 1275)
    
    return self.cleaned_data['metadata']


class TagAdmin(admin.ModelAdmin):
  search_fields = ['name', 'metadata']
  list_filter = ('category',)
  form = TagAdminForm



class CommentAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(CommentAdminForm, self).__init__(*args, **kwargs)
    self.fields['contents'].widget = codemirror_json_widget

  def clean_contents(self):
    try:
      contents = json.loads(self.cleaned_data['contents'])
    except ValueError as e:
      raise forms.ValidationError(u'%s'%e)
      # Expecting property name enclosed in double quotes: line 14 column 5 (char 1275)
    
    return self.cleaned_data['contents']


def make_accepted(modeladmin, request, queryset):
    queryset.update(status=Comment.PRIVATE)

make_accepted.short_description = "Mark selected comments as visible"


class CommentAdmin(admin.ModelAdmin):
  search_fields = ['contents', 'owner']
  list_display = ['date', 'contents', 'owner', 'story', 'status']
  actions = [make_accepted]
  form = CommentAdminForm


class ReviewAdmin(admin.ModelAdmin):
  search_fields = ['contents', 'assignee']
  # list_filter = ('category',)
  #list_display = ['date', 'contents', 'owner', 'story', 'status']
  list_filter = ('status', 'category')
  list_display = ('pk', '__str__', 'category', 'assignee', 'assigned_by',   'status')
  list_display_links = ('pk', '__str__', 'assignee')

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name == "story":
      kwargs["queryset"] = Story.objects.filter(status__in=[Story.EDITING, Story.REVIEW])
    elif db_field.name == "assignee":
      kwargs["queryset"] = User.objects.filter(groups__name__in=['reviewers', 'editors'])
    return super(ReviewAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


  def add_view(self,request,extra_content=None):
    self.exclude = Review.FIELDS + ('contents','assigned_by')
    return super(ReviewAdmin,self).add_view(request)

  # deprecated.
  # def get_readonly_fields(self, request, obj=None):
  #   if obj: # obj is not None, so this is an edit
  #       return ['status',] # Return a list or tuple of readonly fields' names
  #   else: # This is an addition
  #       return []

  def change_view(self,request,object_id,extra_content=None):
    obj = Review.objects.get(pk=object_id)
    if obj.category == Review.EDITING:
      self.exclude = Review.FIELDS
    else:
      self.exclude = []
    return super(ReviewAdmin,self).change_view(request,object_id)

  def save_model(self, request, obj, form, change):
    if not change:
      obj.assigned_by = request.user
    obj.save()

# # Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Caption, CaptionAdmin)
admin.site.register(Mention)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
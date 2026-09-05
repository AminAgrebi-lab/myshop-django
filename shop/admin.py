from django import forms
from django.contrib import admin
from django.utils.translation import get_language

from .models import Category, Product


class CategoryAdminForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    slug = forms.SlugField(max_length=200)

    class Meta:
        model = Category
        fields = ['name', 'slug']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lang = get_language()
            self.initial['name'] = self.instance.safe_translation_getter('name', language_code=lang)
            self.initial['slug'] = self.instance.safe_translation_getter('slug', language_code=lang)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        instance.set_current_language(get_language())
        instance.name = self.cleaned_data['name']
        instance.slug = self.cleaned_data['slug']
        instance.save()
        return instance


class ProductAdminForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    slug = forms.SlugField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'available',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lang = get_language()
            self.initial['name'] = self.instance.safe_translation_getter('name', language_code=lang)
            self.initial['slug'] = self.instance.safe_translation_getter('slug', language_code=lang)
            self.initial['description'] = self.instance.safe_translation_getter(
                'description', default='', language_code=lang
            )

    def save(self, commit=True):
        instance = super().save(commit=commit)
        instance.set_current_language(get_language())
        instance.name = self.cleaned_data['name']
        instance.slug = self.cleaned_data['slug']
        instance.description = self.cleaned_data['description']
        instance.save()
        return instance


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ['id', 'name', 'slug']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['id', 'name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
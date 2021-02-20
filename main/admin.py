from django.contrib import admin
from .models import AdvUser ,SubRubric, SuperRubric, Bulletin, AdditionalImage

from .forms import SubRubricForm


class SubRubricInline(admin.TabularInline):
    model = SubRubric


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class BulletinAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'published') 
    fields = (('rubric', 'author'), 'title', 'content', 'price', 'contacts', 'image', 'is_active') 
    inlines = (AdditionalImageInline,)


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)

class  SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


admin.site.register(Bulletin, BulletinAdmin)
admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(AdvUser)

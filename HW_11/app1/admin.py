from django.contrib import admin

# Register your models here.

from .models import Student, Course, Grade

admin.site.register(Grade)
admin.site.register(Course)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'surname', 'name', 'sex', 'average_grade')
    search_fields = ('name', 'surname')
    list_filter = ('sex', 'active')

    # для формирования slug
    prepopulated_fields = {"slug": ("name", "surname")}

    def short_name(self, obj):
        return f"{obj.surname} {obj.name[0]}."

    def average_grade(self, obj):
        from django.db.models import Avg
        res = Grade.objects.filter(person=obj).aggregate(Avg('grade', default=0))
        return res['grade__avg']

    short_name.short_description = "Короткое имя"


from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, DetailView
from .models import Student
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

menu =  [
    {'menu1':"url1"},
    {'menu2':"url2"},
]

def index(r):
    return render(r, 'index.html')


class StudentsView(ListView):
    model = Student
    template_name = 'students.html'
    context_object_name = 'students'

    def get(self, r, *args, **kwargs):
        f = r.GET.get('f', default='')
        students = Student.objects.filter(name__contains=f).all()
        return render(r, self.template_name, context={'students': students, 'menu': menu})


class StudentView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'student.html'
    slug_url_kwarg = 'name_slug'
    context_object_name = 'student'
    login_url = '/users/login/'

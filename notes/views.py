from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def get_notes(request):

    return render(request, 'hello.html', {'title': 'hello world', 'greeter': 'buzz'})

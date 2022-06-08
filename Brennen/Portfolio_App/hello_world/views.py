from django.shortcuts import render


# Create your views here.
"""
when this function is called, it will render an HTML file called 'hello_world.html'
the view function takes one argument, which is request object(HttpRequestObject) created whenever page is loaded
"""
def hello_world(request):
    return render(request, 'hello_world.html', {})

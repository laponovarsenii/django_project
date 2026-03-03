from django.http import HttpResponse

from django.http import HttpResponse

def hello(request):
    your_name = "Arsenii"
    return HttpResponse(f"Hello {your_name}")


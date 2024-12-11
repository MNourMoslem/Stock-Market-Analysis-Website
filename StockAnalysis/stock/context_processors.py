from django.urls import reverse

def search_url(request):
    return {'search_url': reverse('search_stocks')}
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render_to_response
from aws_req import compute_args
from django.http import HttpResponse
from django.utils.http import urlquote
# Create your views here.
from django.views.decorators.cache import cache_page

@cache_page(1)
def search_view(request, title):
    s = compute_args(str(title),settings.AMAZON_KEY)
    return render_to_response("search_result.html",{'resultat':s})

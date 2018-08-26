from django.shortcuts import render
from .models import Car, Recall, IIHS
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# Create your views here.
def top_ten_list(request):
	return JsonResponse({'status': 200, 'data': 'This is the test to get the top_ten_list of cars'})

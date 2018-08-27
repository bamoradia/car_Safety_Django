from django.shortcuts import render
from .models import Car, Recall, IIHS
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import requests
import json

# Create your views here.

#returns the top ten cars with the highest aggregate score (cars which are already in the database)
def top_ten_list(request):
	return JsonResponse({'status': 200, 'data': 'This is the test to get the top_ten_list of cars'})



# return a list of the years which can be used for the serach
def get_model_years(request):
	if request.method == 'GET':
		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings?format=json')

		print(fetch_response)

		response_json = fetch_response.json()

		def response(x): 
			if x['ModelYear'] < 2100:
				return x['ModelYear']
			else: 
				return 'null' #Trying to return a javascript null

		years = list(map(response, response_json['Results']))

		print(years)

		return JsonResponse({'status': 200, 'data': years})
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot GET /modelyears'})


# return a list of all the makes that were tested for the given year
# Must include a year in the request body
@csrf_exempt
def get_makes(request):
	if request.method == 'POST':
		print(request.POST['year'])

		response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}?format=json'.format(request.POST['year']))

		response_json = response.json()

		def response(x):
			return x['Make']

		makes = list(map(response, response_json['Results']))


		return JsonResponse({'status': 200, 'data': makes})
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /makes'})


# return a list of all models based on model year and make
# Must include model year and make in the request body
@csrf_exempt
def get_models(request):
	if request.method == 'POST':

		return JsonResponse({'status': 200, 'data': 'POSTED'})

	else:
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /models'})



















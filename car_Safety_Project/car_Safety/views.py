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

		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}?format=json'.format(request.POST['year']))

		response_json = fetch_response.json()

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

		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}/make/{}?format=json'.format(request.POST['year'], request.POST['make']))

		response_json = fetch_response.json()

		def response(x):
			return x['Model']

		makes = list(map(response, response_json['Results']))

		return JsonResponse({'status': 200, 'data': makes})

	else:
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /models'})


# return a list of all trims associated with the model year, make, and model
# Must include model year, make, and model in request body
@csrf_exempt
def get_trims(request):
	if request.method == 'POST':

		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}/make/{}/model/{}?format=json'.format(request.POST['year'], request.POST['make'], request.POST['model']))

		response_json = fetch_response.json()

		def response(x):
			return {'trim': x['VehicleDescription'], 'vehicle_id': x['VehicleId']}

		trims = list(map(response, response_json['Results']))

		return JsonResponse({'status': 200, 'data': trims})
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /trims'}) 


# return all the information about a specific vehicle
# must include the vehicle id in the request body
@csrf_exempt
def get_vehicle_info(request):
	if request.method == 'POST':

		response_nhtsa_info = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/VehicleId/{}?format=json'.format(request.POST['vehicleid']))

		response_nhtsa_info_json = response_nhtsa_info.json()

		response_nhtsa_recall = requests.get('https://one.nhtsa.gov/webapi/api/Recalls/vehicle/modelyear/{}/make/{}/model/{}?format=json'.format(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'], response_nhtsa_info_json['Results'][0]['Model']))

		response_nhtsa_recall_json = response_nhtsa_recall.json()

		print(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'])



		response_iihs_vehicle_series = requests.get('https://api.iihs.org/V4/ratings/series/{}/{}?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'].lower()))


		response_iihs_vehicle_series_json = response_iihs_vehicle_series.json()

		for i in range(0, len(response_iihs_vehicle_series_json)):
			index = response_iihs_vehicle_series_json[i]['name'].find(response_nhtsa_info_json['Results'][0]['Model'])
			if index >= 0:
				name_of_vehicle = response_iihs_vehicle_series_json[i]['slug']



		response_iihs_info = requests.get('https://api.iihs.org/V4/ratings/single/{}/{}/{}/?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'].lower(), name_of_vehicle))

		response_iihs_info_json = response_iihs_info.json()




		return JsonResponse({'status': 200, 'data': 'POSTED'})

	else:
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /vehicleinfo'}) 
















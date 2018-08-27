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
	all_cars = Car.objects.get.all()

	# if the datbase only has 10 or less items
	if len(all_cars) <= 10:
		top_ten = all_cars
	else: 
		# will need to sort by safety score and save the top ten in top_ten

		top_ten = 'THIS NEEDS TO BE DONE'


	# after the top_ten list is made, need to find the associated recalls for each of the top ten as well as the IIHS car information and consolidate the information

	

	return JsonResponse({'status': 200, 'data': 'This is the test to get the top_ten_list of cars'})















# return a list of the years which can be used for the serach
def get_model_years(request):
	if request.method == 'GET':
		# make initial request to get all model years from nhtsa
		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings?format=json')

		response_json = fetch_response.json()

		# clean data to only include real years
		def response(x): 
			if x['ModelYear'] < 2100:
				return x['ModelYear']
			else: 
				return 'null' #Trying to return a javascript null

		# make a new list that only contains the years
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
		# make request to nhtsa to find all makes assiciated with a specific model year
		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}?format=json'.format(request.POST['year']))

		response_json = fetch_response.json()

		# only return the make
		def response(x):
			return x['Make']
		# make a new list that only contains the makes 
		makes = list(map(response, response_json['Results']))


		return JsonResponse({'status': 200, 'data': makes})
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /makes'})















# return a list of all models based on model year and make
# Must include model year and make in the request body
@csrf_exempt
def get_models(request):
	if request.method == 'POST':
		# makee initial request to nhtsa to find all models associated with a model year and make
		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}/make/{}?format=json'.format(request.POST['year'], request.POST['make']))

		response_json = fetch_response.json()
		# only return the model names
		def response(x):
			return x['Model']
		# make a new list that only contains the models
		makes = list(map(response, response_json['Results']))

		return JsonResponse({'status': 200, 'data': makes})

	else:
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /models'})















# return a list of all trims associated with the model year, make, and model
# Must include model year, make, and model in request body
@csrf_exempt
def get_trims(request):
	if request.method == 'POST':
		# make a request to nhtsa to get all the trims associated with a model year, make and model
		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}/make/{}/model/{}?format=json'.format(request.POST['year'], request.POST['make'], request.POST['model']))

		response_json = fetch_response.json()
		# return the model trim name and the vehicle id
		def response(x):
			return {'trim': x['VehicleDescription'], 'vehicle_id': x['VehicleId']}
		# make a new list that only contains the vehicle name and id
		trims = list(map(response, response_json['Results']))

		return JsonResponse({'status': 200, 'data': trims})
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /trims'}) 















# return all the information about a specific vehicle
# must include the vehicle id in the request body
@csrf_exempt
def get_vehicle_info(request):
	if request.method == 'POST':

		# make first request to nhtsa to get information about specific model
		response_nhtsa_info = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/VehicleId/{}?format=json'.format(request.POST['vehicleid']))

		response_nhtsa_info_json = response_nhtsa_info.json()

		# use response from nhsta to make another request to get recall information about vehicle
		response_nhtsa_recall = requests.get('https://one.nhtsa.gov/webapi/api/Recalls/vehicle/modelyear/{}/make/{}/model/{}?format=json'.format(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'], response_nhtsa_info_json['Results'][0]['Model']))

		response_nhtsa_recall_json = response_nhtsa_recall.json()

		# use basic information to make request to iihs to find all vehicle series associated with that year and model
		response_iihs_vehicle_series = requests.get('https://api.iihs.org/V4/ratings/series/{}/{}?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'].lower()))


		response_iihs_vehicle_series_json = response_iihs_vehicle_series.json()

		# search the models returned to match model name from nhtsa
		for i in range(0, len(response_iihs_vehicle_series_json)):
			index = response_iihs_vehicle_series_json[i]['name'].find(response_nhtsa_info_json['Results'][0]['Model'])
			if index >= 0:
				# if match is found, save slug name (which is used to make next request)
				name_of_vehicle = response_iihs_vehicle_series_json[i]['slug']


		# make request to iihs for full vehicle information based on slug name found above
		response_iihs_info = requests.get('https://api.iihs.org/V4/ratings/single/{}/{}/{}/?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(response_nhtsa_info_json['Results'][0]['ModelYear'], response_nhtsa_info_json['Results'][0]['Make'].lower(), name_of_vehicle))

		response_iihs_info_json = response_iihs_info.json()




		return JsonResponse({'status': 200, 'data': {'nhtsa': response_nhtsa_info_json['Results'][0], 'recall': response_nhtsa_recall_json['Results'], 'iihs': response_iihs_info_json[0]}})

	else:
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /vehicleinfo'}) 






























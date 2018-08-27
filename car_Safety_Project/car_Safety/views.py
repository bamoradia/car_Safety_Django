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

		# check if vehicle exists in the database
		car_nhtsa = Car.objects.filter(vehicle_id=int(request.POST['vehicleid'])).exists()

		if not car_nhtsa:
			# this happens if the vehicle is not in the database
			# make first request to nhtsa to get information about specific model
			response_nhtsa_info = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/VehicleId/{}?format=json'.format(request.POST['vehicleid']))

			nhtsa_info_json = response_nhtsa_info.json()

			# use response from nhsta to make another request to get recall information about vehicle
			nhtsa_recall = requests.get('https://one.nhtsa.gov/webapi/api/Recalls/vehicle/modelyear/{}/make/{}/model/{}?format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'], nhtsa_info_json['Results'][0]['Model']))

			nhtsa_recall_json = nhtsa_recall.json()

			# use basic information to make request to iihs to find all vehicle series associated with that year and model
			iihs_vehicle_series = requests.get('https://api.iihs.org/V4/ratings/series/{}/{}?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'].lower()))


			iihs_vehicle_series_json = iihs_vehicle_series.json()

			# search the models returned to match model name from nhtsa
			for i in range(0, len(iihs_vehicle_series_json)):
				index = iihs_vehicle_series_json[i]['name'].find(nhtsa_info_json['Results'][0]['Model'])
				if index >= 0:
					# if match is found, save slug name (which is used to make next request)
					name_of_vehicle = iihs_vehicle_series_json[i]['slug']


			# make request to iihs for full vehicle information based on slug name found above
			iihs_info = requests.get('https://api.iihs.org/V4/ratings/single/{}/{}/{}/?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'].lower(), name_of_vehicle))

			iihs_info_json = iihs_info.json()



			# -------------------SAVING CAR MODEL------------------------- #

			car_instance = Car(
				model_year= nhtsa_info_json['Results'][0]['ModelYear'],
				make= nhtsa_info_json['Results'][0]['Make'],
				model= nhtsa_info_json['Results'][0]['Model'],
				safety_score= '00',
				vehicle_description= nhtsa_info_json['Results'][0]['VehicleDescription'],
				vehicle_id= nhtsa_info_json['Results'][0]['VehicleId'],
				overall_rating= nhtsa_info_json['Results'][0]['OverallRating'],
				overall_front_crash_rating= nhtsa_info_json['Results'][0]['OverallFrontCrashRating'],
				front_crash_driverside_rating= nhtsa_info_json['Results'][0]['FrontCrashDriversideRating'],
				front_crash_passengerside_rating= nhtsa_info_json['Results'][0]['FrontCrashPassengersideRating'],
				overall_side_crash_rating= nhtsa_info_json['Results'][0]['OverallSideCrashRating'],
				side_crash_driverside_rating= nhtsa_info_json['Results'][0]['SideCrashDriversideRating'],
				side_crash_passengerside_rating= nhtsa_info_json['Results'][0]['SideCrashPassengersideRating'],
				rollover_rating= nhtsa_info_json['Results'][0]['RolloverRating'],
				side_pole_crash_rating= nhtsa_info_json['Results'][0]['SidePoleCrashRating']
			)

			car_instance.save()

			# -------------------SAVING CAR MODEL------------------------- #
			# -------------------SAVING RECALL MODEL---------------------- #

			all_recalls = []

			if len(nhtsa_recall_json['Results']) == 0:
				recall = Recall(
					car= car_instance,
					manufacturer= 'NA',
					component= 'NA',
					consequence= 'NA',
					summary= 'NA',
					remedy= 'NA',
					notes= 'NA',
					model_year= 'NA',
					make= 'NA',
					model= 'NA',
					report_received_date= 'NA',
					nhtsa_campaign_number= 'NA'
				)
				recall.save()

				all_recalls.append(recall)

			else:
				for i in range(0, len(nhtsa_recall_json['Results'])):

					recall = Recall(
						car= car_instance,
						manufacturer= nhtsa_recall_json['Results'][i]['Manufacturer'],
						component= nhtsa_recall_json['Results'][i]['Component'],
						consequence= nhtsa_recall_json['Results'][i]['Consequence'],
						summary= nhtsa_recall_json['Results'][i]['Summary'],
						remedy= nhtsa_recall_json['Results'][i]['Remedy'],
						notes= nhtsa_recall_json['Results'][i]['Notes'],
						model_year= nhtsa_recall_json['Results'][i]['ModelYear'],
						make= nhtsa_recall_json['Results'][i]['Make'],
						model= nhtsa_recall_json['Results'][i]['Model'],
						report_received_date= nhtsa_recall_json['Results'][i]['ReportReceivedDate'],
						nhtsa_campaign_number= nhtsa_recall_json['Results'][i]['NHTSACampaignNumber']
					)
					recall.save()

					all_recalls.append(recall)


			# -------------------SAVING RECALL MODEL---------------------- #
			# -------------------SAVING IIHS MODEL------------------------ #

			iihs = IIHS(
					car= car_instance,
					iihs_id= iihs_info_json[0]['id'],
					vehicle_description= nhtsa_info_json['Results'][0]['VehicleDescription'],
					model_year= iihs_info_json[0]['modelYear'],
					make= iihs_info_json[0]['make']['name'],
					model= iihs_info_json[0]['name'],
					class_name= iihs_info_json[0]['class']['name'],
					top_safety_pick= iihs_info_json[0]['topSafetyPick']['isTopSafetyPickPlus'],
					tsp_year= iihs_info_json[0]['topSafetyPick']['tspYear'],
					tsp_is_qualified= iihs_info_json[0]['topSafetyPick']['isQualified'],
					tsp_built_after= iihs_info_json[0]['topSafetyPick']['builtAfter'],
					tsp_qualifying_text= iihs_info_json[0]['topSafetyPick']['qualifyingText'],
					frmo_qualifying_text= iihs_info_json[0]['frontalRatingsModerateOverlap'][0]['qualifyingText'],
					frmo_built_before= iihs_info_json[0]['frontalRatingsModerateOverlap'][0]['builtBefore'],
					frmo_built_after= iihs_info_json[0]['frontalRatingsModerateOverlap'][0]['builtAfter'],
					frmo_overall_rating= iihs_info_json[0]['frontalRatingsModerateOverlap'][0]['overallRating'],
					frso_qualifying_text= iihs_info_json[0]['frontalRatingsSmallOverlap'][0]['qualifyingText'],
					frso_built_before= iihs_info_json[0]['frontalRatingsSmallOverlap'][0]['builtBefore'],
					frso_built_after= iihs_info_json[0]['frontalRatingsSmallOverlap'][0]['builtAfter'],
					frso_overall_rating= iihs_info_json[0]['frontalRatingsSmallOverlap'][0]['overallRating'],
					frsop_qualifying_text= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['qualifyingText'],
					frsop_built_before= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['builtBefore'],
					frsop_built_after= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['builtAfter'],
					frsop_overall_rating= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['overallRating'],
					sr_qualifying_text= iihs_info_json[0]['sideRatings'][0]['qualifyingText'],
					sr_built_before= iihs_info_json[0]['sideRatings'][0]['builtBefore'],
					sr_built_after= iihs_info_json[0]['sideRatings'][0]['builtAfter'],
					sr_overall_rating= iihs_info_json[0]['sideRatings'][0]['overallRating'], 
					rollover_qualifying_text= iihs_info_json[0]['rolloverRatings'][0]['qualifyingText'],
					rollover_built_before= iihs_info_json[0]['rolloverRatings'][0]['builtBefore'],
					rollover_built_after= iihs_info_json[0]['rolloverRatings'][0]['builtAfter'],
					rollover_overall_rating= iihs_info_json[0]['rolloverRatings'][0]['overallRating'],
					rear_qualifying_text= iihs_info_json[0]['rearRatings'][0]['qualifyingText'],
					rear_built_before= iihs_info_json[0]['rearRatings'][0]['builtBefore'], 
					rear_built_after= iihs_info_json[0]['rearRatings'][0]['builtAfter'],
					rear_overall_rating= iihs_info_json[0]['rearRatings'][0]['overallRating'],
					fcpr_qualifying_text= iihs_info_json[0]['frontCrashPreventionRatings'][0]['qualifyingText'],
					fcpr_built_before= iihs_info_json[0]['frontCrashPreventionRatings'][0]['builtBefore'],
					fcpr_built_after= iihs_info_json[0]['frontCrashPreventionRatings'][0]['builtAfter'],
					fcpr_total_points= iihs_info_json[0]['frontCrashPreventionRatings'][0]['overallRating']['totalPoints'],
					fcpr_rating_text= iihs_info_json[0]['frontCrashPreventionRatings'][0]['overallRating']['ratingText']
				)

			iihs.save()

			# -------------------SAVING IIHS MODEL------------------------ #


			return JsonResponse({'status': 200, 'data': {'nhtsa': [nhtsa_info_json['Results'][0]], 'recall': nhtsa_recall_json['Results'], 'iihs': [iihs_info_json[0]]}})


		else: 
			car_nhtsa = Car.objects.get(vehicle_id=int(request.POST['vehicleid']))
			# vehicle was found in the database
			iihs = IIHS.objects.get(car=car_nhtsa)
			recall = Recall.objects.filter(car=car_nhtsa)




			car_serialized1 = serializers.serialize('json', [car_nhtsa])
			iihs_serialized1 = serializers.serialize('json', [iihs])
			recall_serialized1 = serializers.serialize('json', recall)

			car_serialized = json.loads(car_serialized1)
			iihs_serialized = json.loads(iihs_serialized1)
			recall_serialized = json.loads(recall_serialized1)


			return JsonResponse({'status': 200, 'data': {'nhtsa': car_serialized, 'recall': recall_serialized, 'iihs': iihs_serialized}})
	else:
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /vehicleinfo'}) 






























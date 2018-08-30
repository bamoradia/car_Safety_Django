from django.shortcuts import render
from .models import Car, Recall, IIHS
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import requests
import json

def filterCars(IIHS_input):
	if IIHS_input.top_safety_pick == 'True':
		return IIHS_input





#returns the top ten cars with the highest aggregate score (cars which are already in the database)
def top_safety(request):
	all_IIHS_cars = IIHS.objects.all()

	top_safety_picks = list(filter(filterCars, all_IIHS_cars))

	car_nhtsa = []
	recall = []


	for i in range(0, len(top_safety_picks)):
		found_car = Car.objects.get(vehicle_description=top_safety_picks[i].vehicle_description)
		car_recall = Recall.objects.filter(car=found_car)
		recall_serialized = serializers.serialize('json', car_recall)
		car_nhtsa.append(found_car)
		recall.append(recall_serialized)

	car_serialized1 = serializers.serialize('json', car_nhtsa)
	iihs_serialized1 = serializers.serialize('json', top_safety_picks)
	# recall_serialized1 = serializers.serialize('json', recall)

	# print('this is the serialized recall', recall[0])

	car_serialized = json.loads(car_serialized1)
	iihs_serialized = json.loads(iihs_serialized1)
	# recall_serialized = json.loads(recall_serialized1)

	# return JsonResponse({'status': 200, 'data': {'iihs':iihs_serialized, 'nhtsa': car_serialized}})

	return JsonResponse({'status': 200, 'data': {'nhtsa': car_serialized, 'recall': recall, 'iihs': iihs_serialized}})















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

		return JsonResponse({'status': 200, 'data': years})
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot GET /modelyears'})















# return a list of all the makes that were tested for the given year
# Must include a year in the request body
@csrf_exempt
def get_makes(request):
	if request.method == 'POST':
		# make request to nhtsa to find all makes assiciated with a specific model year

		parsedData = json.loads(request.body)

		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}?format=json'.format(parsedData['year']))

		response_json = fetch_response.json()

		# only return the make
		def response(x):
			return x['Make']
		# make a new list that only contains the makes 
		makes = list(map(response, response_json['Results']))


		return JsonResponse({'status': 200, 'data': makes })
	else: 
		return JsonResponse({'status': 400, 'data': 'Cannot POST to /makes'})















# return a list of all models based on model year and make
# Must include model year and make in the request body
@csrf_exempt
def get_models(request):
	if request.method == 'POST':
		# makee initial request to nhtsa to find all models associated with a model year and make
		parsedData = json.loads(request.body)

		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}/make/{}?format=json'.format(parsedData['year'], parsedData['make']))

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

		parsedData = json.loads(request.body)
		# make a request to nhtsa to get all the trims associated with a model year, make and model
		fetch_response = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/modelyear/{}/make/{}/model/{}?format=json'.format(parsedData['year'], parsedData['make'], parsedData['model']))

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

		parsedData = json.loads(request.body)
		# check if vehicle exists in the database
		car_nhtsa = Car.objects.filter(vehicle_id=int(parsedData['vehicleid'])).exists()

		if not car_nhtsa:
			# this happens if the vehicle is not in the database
			# make first request to nhtsa to get information about specific model
			response_nhtsa_info = requests.get('https://one.nhtsa.gov/webapi/api/SafetyRatings/VehicleId/{}?format=json'.format(parsedData['vehicleid']))

			nhtsa_info_json = response_nhtsa_info.json()

			# use response from nhsta to make another request to get recall information about vehicle
			nhtsa_recall = requests.get('https://one.nhtsa.gov/webapi/api/Recalls/vehicle/modelyear/{}/make/{}/model/{}?format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'], nhtsa_info_json['Results'][0]['Model']))

			nhtsa_recall_json = nhtsa_recall.json()

			# use basic information to make request to iihs to find all vehicle series associated with that year and model
			iihs_vehicle_series = requests.get('https://api.iihs.org/V4/ratings/series/{}/{}?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'].lower()))


			iihs_vehicle_series_json = iihs_vehicle_series.json()

			# search the models returned to match model name from nhtsa
			for i in range(0, len(iihs_vehicle_series_json)):
				iihs_name = iihs_vehicle_series_json[i]['name'].lower()
				nhtsa_name = nhtsa_info_json['Results'][0]['Model'].lower()
				index = iihs_name.find(nhtsa_name)
				if index >= 0:
					# if match is found, save slug name (which is used to make next request)
					name_of_vehicle = iihs_vehicle_series_json[i]['slug']


			# make request to iihs for full vehicle information based on slug name found above
			iihs_info = requests.get('https://api.iihs.org/V4/ratings/single/{}/{}/{}/?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'].lower(), name_of_vehicle))

			print('https://api.iihs.org/V4/ratings/single/{}/{}/{}/?apikey=uZBIc3DS8k6evZTw62xttB2dkklf-3ZCqVRpT6CCKP4&format=json'.format(nhtsa_info_json['Results'][0]['ModelYear'], nhtsa_info_json['Results'][0]['Make'].lower(), name_of_vehicle))

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
						consequence= nhtsa_recall_json['Results'][i]['Conequence'],
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

			# Save only the data set which has is_primary as true
			iihs = IIHS(
					car= car_instance,
					iihs_id= iihs_info_json[0]['id'],
					vehicle_description= nhtsa_info_json['Results'][0]['VehicleDescription'],
					model_year= iihs_info_json[0]['modelYear'],
					make= iihs_info_json[0]['make']['name'],
					model= iihs_info_json[0]['name'],
					class_name= iihs_info_json[0]['class']['name']
			)
			iihs.save()


			# -------------------TOP SAFETY PICK------------------------ #
			if iihs_info_json[0]['topSafetyPick'] == None:
				iihs.top_safety_pick= None
				iihs.tsp_year= None
				iihs.tsp_is_qualified= None
				iihs.tsp_built_after= None
				iihs.tsp_qualifying_text= None

			else:
				iihs.top_safety_pick= iihs_info_json[0]['topSafetyPick']['isTopSafetyPickPlus']
				iihs.tsp_year= iihs_info_json[0]['topSafetyPick']['tspYear']
				iihs.tsp_is_qualified= iihs_info_json[0]['topSafetyPick']['isQualified']
				iihs.tsp_built_after= iihs_info_json[0]['topSafetyPick']['builtAfter']
				iihs.tsp_qualifying_text= iihs_info_json[0]['topSafetyPick']['qualifyingText']


			# -------------------Frontal Ratings Moderate Overlap------------------------ #
			if iihs_info_json[0]['frontalRatingsModerateOverlap'] == None:
				iihs.frmo_qualifying_text= None
				iihs.frmo_built_before= None
				iihs.frmo_built_after= None
				iihs.frmo_overall_rating= None
			else: 
				for i in range(0, len(iihs_info_json[0]['frontalRatingsModerateOverlap'])):
					if iihs_info_json[0]['frontalRatingsModerateOverlap'][i]['isPrimary']:
						iihs.frmo_qualifying_text= iihs_info_json[0]['frontalRatingsModerateOverlap'][i]['qualifyingText']
						iihs.frmo_built_before= iihs_info_json[0]['frontalRatingsModerateOverlap'][i]['builtBefore']
						iihs.frmo_built_after= iihs_info_json[0]['frontalRatingsModerateOverlap'][i]['builtAfter']
						iihs.frmo_overall_rating= iihs_info_json[0]['frontalRatingsModerateOverlap'][i]['overallRating']


			# -------------------Frontal Ratings Small Overlap------------------------ #
			if iihs_info_json[0]['frontalRatingsSmallOverlap'] == None:
				frso_qualifying_text= None
				frso_built_before= None
				frso_built_after= None
				frso_overall_rating= None
			else: 
				for i in range(0, len(iihs_info_json[0]['frontalRatingsSmallOverlap'])):
					if iihs_info_json[0]['frontalRatingsSmallOverlap'][i]['isPrimary']:
						iihs.frso_qualifying_text= iihs_info_json[0]['frontalRatingsSmallOverlap'][i]['qualifyingText']
						iihs.frso_built_before= iihs_info_json[0]['frontalRatingsSmallOverlap'][i]['builtBefore']
						iihs.frso_built_after= iihs_info_json[0]['frontalRatingsSmallOverlap'][i]['builtAfter']
						iihs.frso_overall_rating= iihs_info_json[0]['frontalRatingsSmallOverlap'][i]['overallRating']


			# -------------------Frontal Ratings Small Overlap Passenger------------------------ #
			if iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'] == None:
				iihs.frsop_qualifying_text= None
				iihs.frsop_built_before= None
				iihs.frsop_built_after= None
				iihs.frsop_overall_rating= None
			else: 
				for i in range(0, len(iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'])):
					if iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][i]['isPrimary']:
						iihs.frsop_qualifying_text= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['qualifyingText']
						iihs.frsop_built_before= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['builtBefore']
						iihs.frsop_built_after= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['builtAfter']
						iihs.frsop_overall_rating= iihs_info_json[0]['frontalRatingsSmallOverlapPassenger'][0]['overallRating']


			# -------------------Side Ratings------------------------ #
			if iihs_info_json[0]['sideRatings'] == None:
				iihs.sr_qualifying_text= None
				iihs.sr_built_before= None
				iihs.sr_built_after= None
				iihs.sr_overall_rating= None
			else:
				for i in range(0, len(iihs_info_json[0]['sideRatings'])):
					if iihs_info_json[0]['sideRatings'][i]['isPrimary']:
						iihs.sr_qualifying_text= iihs_info_json[0]['sideRatings'][0]['qualifyingText']
						iihs.sr_built_before= iihs_info_json[0]['sideRatings'][0]['builtBefore']
						iihs.sr_built_after= iihs_info_json[0]['sideRatings'][0]['builtAfter']
						iihs.sr_overall_rating= iihs_info_json[0]['sideRatings'][0]['overallRating']


			# -------------------Rollover Ratings------------------------ #
			if iihs_info_json[0]['rolloverRatings'] == None:
					iihs.rollover_qualifying_text= None
					iihs.rollover_built_before= None
					iihs.rollover_built_after= None
					iihs.rollover_overall_rating= None
			else:
				for i in range(0, len(iihs_info_json[0]['rolloverRatings'])):
					if iihs_info_json[0]['rolloverRatings'][i]['isPrimary']:
						iihs.rollover_qualifying_text= iihs_info_json[0]['rolloverRatings'][0]['qualifyingText']
						iihs.rollover_built_before= iihs_info_json[0]['rolloverRatings'][0]['builtBefore']
						iihs.rollover_built_after= iihs_info_json[0]['rolloverRatings'][0]['builtAfter']
						iihs.rollover_overall_rating= iihs_info_json[0]['rolloverRatings'][0]['overallRating']


			# -------------------Rear Ratings------------------------ #
			if iihs_info_json[0]['rearRatings'] == None:
				iihs.rear_qualifying_text= None
				iihs.rear_built_before= None
				iihs.rear_built_after= None
				iihs.rear_overall_rating= None
			else:
				for i in range(0, len(iihs_info_json[0]['rearRatings'])):
					if iihs_info_json[0]['rearRatings'][i]['isPrimary']:
						iihs.rear_qualifying_text= iihs_info_json[0]['rearRatings'][0]['qualifyingText']
						iihs.rear_built_before= iihs_info_json[0]['rearRatings'][0]['builtBefore']
						iihs.rear_built_after= iihs_info_json[0]['rearRatings'][0]['builtAfter']
						iihs.rear_overall_rating= iihs_info_json[0]['rearRatings'][0]['overallRating']


			# -------------------Rear Ratings------------------------ #
			if iihs_info_json[0]['rearRatings'] == None:
					iihs.fcpr_qualifying_text= None
					iihs.fcpr_built_before= None
					iihs.fcpr_built_after= None
					iihs.fcpr_total_points= None
					iihs.fcpr_rating_text= None
			else:
				for i in range(0, len(iihs_info_json[0]['frontCrashPreventionRatings'])):
					if iihs_info_json[0]['frontCrashPreventionRatings'][i]['isPrimary']:
						iihs.fcpr_qualifying_text= iihs_info_json[0]['frontCrashPreventionRatings'][0]['qualifyingText']
						iihs.fcpr_built_before= iihs_info_json[0]['frontCrashPreventionRatings'][0]['builtBefore']
						iihs.fcpr_built_after= iihs_info_json[0]['frontCrashPreventionRatings'][0]['builtAfter']
						iihs.fcpr_total_points= iihs_info_json[0]['frontCrashPreventionRatings'][0]['overallRating']['totalPoints']
						iihs.fcpr_rating_text= iihs_info_json[0]['frontCrashPreventionRatings'][0]['overallRating']['ratingText']

			iihs.save()


			# -------------------SAVING IIHS MODEL------------------------ #

			car_serialized1 = serializers.serialize('json', [car_instance])
			iihs_serialized1 = serializers.serialize('json', [iihs])
			recall_serialized1 = serializers.serialize('json', all_recalls)

			car_serialized = json.loads(car_serialized1)
			iihs_serialized = json.loads(iihs_serialized1)
			recall_serialized = json.loads(recall_serialized1)

			return JsonResponse({'status': 200, 'data': {'nhtsa': car_serialized, 'recall': recall_serialized, 'iihs': iihs_serialized}})


		else: 
			car_nhtsa = Car.objects.get(vehicle_id=int(parsedData['vehicleid']))
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






























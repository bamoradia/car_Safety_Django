from django.db import models

# Create your models here.


class Car(models.Model):
	model_year = models.IntegerField()
	make = models.CharField(max_length=32)
	model = models.CharField(max_length=32)
	safety_score = models.CharField(max_length=8, default='NA')
	vehicle_id = models.IntegerField()
	vehicle_description = models.CharField(max_length=64)
	overall_rating = models.CharField(max_length=16)
	overall_front_crash_rating = models.CharField(max_length=16)
	front_crash_driverside_rating = models.CharField(max_length=16)
	front_crash_passengerside_rating = models.CharField(max_length=16)
	overall_side_crash_rating = models.CharField(max_length=16)
	side_crash_driverside_rating = models.CharField(max_length=16)
	side_crash_passengerside_rating = models.CharField(max_length=16)
	rollover_rating = models.CharField(max_length=16)
	side_pole_crash_rating = models.CharField(max_length=16)
	complaints = models.CharField(max_length=8, default='NA')



	def __str__(self):
		return self.vehicle_description


class Recall(models.Model):
	car = models.ForeignKey(Car, on_delete=models.CASCADE)
	manufacturer = models.CharField(max_length=64)
	component = models.TextField()
	consequence = models.TextField()
	summary = models.TextField()
	remedy = models.TextField()
	notes = models.TextField()
	model_year = models.CharField(max_length=8)
	make = models.CharField(max_length=32)
	model = models.CharField(max_length=32)
	report_received_date = models.CharField(max_length=32)
	nhtsa_campaign_number = models.CharField(max_length=16)


	def __str__(self):
		return self.car.vehicle_description



class IIHS(models.Model):
	car = models.OneToOneField(Car, on_delete=models.CASCADE)
	iihs_id = models.IntegerField()
	vehicle_description = models.CharField(max_length=64)
	model_year = models.IntegerField()
	make = models.CharField(max_length=32)
	model = models.CharField(max_length=32)
	class_name = models.CharField(max_length=32)
	top_safety_pick = models.CharField(max_length=8, null=True)
	tsp_year = models.CharField(max_length=8, null=True)
	tsp_is_qualified = models.CharField(max_length=8, null=True)
	tsp_built_after = models.CharField(max_length=32, null=True)
	tsp_qualifying_text = models.TextField(null=True)
	frmo_qualifying_text = models.TextField(null=True)
	frmo_built_before = models.CharField(max_length=32, null=True)
	frmo_built_after = models.CharField(max_length=32, null=True)
	frmo_overall_rating = models.CharField(max_length=32, null=True)
	frso_qualifying_text = models.TextField(null=True)
	frso_built_before = models.CharField(max_length=32, null=True)
	frso_built_after = models.CharField(max_length=32, null=True)
	frso_overall_rating = models.CharField(max_length=32, null=True)
	frsop_qualifying_text = models.TextField(null=True)
	frsop_built_before = models.CharField(max_length=32, null=True)
	frsop_built_after = models.CharField(max_length=32, null=True)
	frsop_overall_rating = models.CharField(max_length=32, null=True)
	sr_qualifying_text = models.TextField(null=True)
	sr_built_before = models.CharField(max_length=32, null=True)
	sr_built_after = models.CharField(max_length=32, null=True)
	sr_overall_rating = models.CharField(max_length=32, null=True)
	rollover_qualifying_text = models.TextField(null=True)
	rollover_built_before = models.CharField(max_length=32, null=True)
	rollover_built_after = models.CharField(max_length=32, null=True)
	rollover_overall_rating = models.CharField(max_length=32, null=True)
	rear_qualifying_text = models.TextField(null=True)
	rear_built_before = models.CharField(max_length=32, null=True)
	rear_built_after = models.CharField(max_length=32, null=True)
	rear_overall_rating = models.CharField(max_length=32, null=True)
	fcpr_qualifying_text = models.TextField(null=True)
	fcpr_built_before = models.CharField(max_length=32, null=True)
	fcpr_built_after = models.CharField(max_length=32, null=True)
	fcpr_total_points = models.CharField(max_length=4, null=True)
	fcpr_rating_text = models.TextField(null=True)


	def __str__(self):
		return self.car.vehicle_description






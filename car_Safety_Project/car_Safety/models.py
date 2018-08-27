from django.db import models

# Create your models here.


class Car(models.Model):
	model_year = models.IntegerField()
	make = models.CharField(max_length=32)
	model = models.CharField(max_length=32)
	safety_score = models.CharField(max_length=8, default='00')
	vehicle_id = models.IntegerField()
	vehicle_description = models.CharField(max_length=64)
	overall_rating = models.CharField(max_length=4)
	overall_front_crash_rating = models.CharField(max_length=4)
	front_crash_driverside_rating = models.CharField(max_length=4)
	front_crash_passengerside_rating = models.CharField(max_length=4)
	overall_side_crash_rating = models.CharField(max_length=4)
	side_crash_driverside_rating = models.CharField(max_length=4)
	side_crash_passengerside_rating = models.CharField(max_length=4)
	rollover_rating = models.CharField(max_length=4)
	side_pole_crash_rating = models.CharField(max_length=4)



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



class IIHS(models.Model):
	car = models.OneToOneField(Car, on_delete=models.CASCADE)
	iihs_id = models.IntegerField()
	vehicle_description = models.CharField(max_length=64)
	model_year = models.IntegerField()
	make = models.CharField(max_length=32)
	model = models.CharField(max_length=32)
	class_name = models.CharField(max_length=32)
	top_safety_pick = models.BooleanField()
	tsp_year = models.CharField(max_length=8)
	tsp_is_qualified = models.BooleanField()
	tsp_built_after = models.CharField(max_length=32)
	tsp_qualifying_text = models.TextField()
	frmo_qualifying_text = models.TextField()
	frmo_built_before = models.CharField(max_length=32)
	frmo_built_after = models.CharField(max_length=32)
	frmo_overall_rating = models.CharField(max_length=32)
	frso_qualifying_text = models.TextField()
	frso_built_before = models.CharField(max_length=32)
	frso_built_after = models.CharField(max_length=32)
	frso_overall_rating = models.CharField(max_length=32)
	frsop_qualifying_text = models.TextField()
	frsop_built_before = models.CharField(max_length=32)
	frsop_built_after = models.CharField(max_length=32)
	frsop_overall_rating = models.CharField(max_length=32)
	sr_qualifying_text = models.TextField()
	sr_built_before = models.CharField(max_length=32)
	sr_built_after = models.CharField(max_length=32)
	sr_overall_rating = models.CharField(max_length=32)
	rollover_qualifying_text = models.TextField()
	rollover_built_before = models.CharField(max_length=32)
	rollover_built_after = models.CharField(max_length=32)
	rollover_overall_rating = models.CharField(max_length=32)
	rear_qualifying_text = models.TextField()
	rear_built_before = models.CharField(max_length=32)
	rear_built_after = models.CharField(max_length=32)
	rear_overall_rating = models.CharField(max_length=32)
	fcpr_qualifying_text = models.TextField()
	fcpr_built_before = models.CharField(max_length=32)
	fcpr_built_after = models.CharField(max_length=32)
	fcpr_total_points = models.CharField(max_length=4)
	fcpr_rating_text = models.TextField()







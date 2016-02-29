from django.db import models

class Area(models.Model):
	Area_id = models.IntegerField(primary_key=True)
	Area_name = models.CharField(max_length = 10)

class Attraction(models.Model):
	Attr_id = models.IntegerField(primary_key=True)
	Attr_name = models.CharField(max_length=20)
	Attr_longitude = models.FloatField()
	Attr_latitude = models.FloatField()
	Attr_address = models.CharField(max_length=30)
	Attr_tel = models.CharField(max_length=30,null=True)
	Attr_opentime = models.CharField(max_length=10,null=True)
	Attr_endtime = models.CharField(max_length=10,null=True)
	Attr_stay1 = models.IntegerField(null=True)
	Attr_stay2 = models.IntegerField(null=True)
	Attr_stay3 = models.IntegerField(null=True)
	Attr_hot = models.IntegerField()
	Attr_icon = models.IntegerField()
	Area = models.ForeignKey(Area)
	
		
class Comment(models.Model):
	C_id = models.IntegerField(primary_key=True)
	C_date = models.IntegerField()
	C_content = models.CharField(max_length=500)
	Attr = models.ForeignKey(Attraction)
		
class Article(models.Model):
	A_id = models.IntegerField(primary_key=True)
	A_date = models.CharField(max_length=100,null=True)
	A_name = models.CharField(max_length=100,null=True)
	A_content = models.CharField(max_length=3000,null=True)
	A_url = models.CharField(max_length=100,null=True)
	A_source = models.CharField(max_length=10,null=True)
	attr_in_art_count = models.IntegerField(null=True)
		
class Art_To_Att(models.Model):
	Attr = models.ForeignKey(Attraction)
	Article = models.ForeignKey(Article)
	
class Tag(models.Model):
	T_name = models.CharField(max_length=20)
	T_count = models.IntegerField(null=True)
	
class Tag_To_Att(models.Model):
	Attr = models.ForeignKey(Attraction)
	tag = models.ForeignKey(Tag)

class weather(models.Model):
	W_year = models.IntegerField()
	W_month = models.IntegerField()
	W_day = models.IntegerField()
	W_hitemp = models.FloatField()
	W_lowtemp = models.FloatField()

class apriori(models.Model):
	ap_id = models.IntegerField()
	Attr = models.ForeignKey(Attraction)

class Text_Cloud(models.Model):
	TC_name = models.CharField(max_length=20)
	TC_count = models.IntegerField()

class Text_Cloud_Att(models.Model):
	TC = models.ForeignKey(Text_Cloud)
	Attr = models.ForeignKey(Attraction)
	



	
from django.db import models
from django.contrib.auth.models import User
class Author(models.Model):
	name = models.CharField(max_length = 32)
	user = models.OneToOneField(User, on_delete=models.CASCADE,null =True)

	def __str__(self):
		return u'%s' % (self.name)
	
class Story(models.Model):
	headline = models.CharField(max_length = 64)
	CATEGORIES = [('pol','Politics'),('art','Art'),('tech','Technology'),('trivia','Trivial News')]
	category = models.CharField(max_length = 32,choices = CATEGORIES,default = 'unknown')
	REGIONS = [('eu','Europe'),('uk','United Kingdom'),('w','World News')]
	region = models.CharField(max_length = 32,choices = REGIONS)
	author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
	date = models.DateField()
	details = models.CharField(max_length = 128)

	def __str__(self):
		return u'%s (%s)' % (self.headline, self.region)

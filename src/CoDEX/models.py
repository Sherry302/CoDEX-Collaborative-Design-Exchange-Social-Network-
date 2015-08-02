from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User
from datetime import datetime


class Uploaded_image(models.Model):
	image = models.FileField(upload_to="media")
	image_type = models.CharField(max_length=50) 
	def __unicode__(self):
		return self.image.url

class Tag(models.Model): 
	name = models.CharField(max_length=20)
	num_posts = models.SmallIntegerField() 

	def __unicode__(self):
		return self.name

class Design_Request(models.Model):
	title = models.CharField(max_length=100)
	text = models.CharField(max_length=5000)
	user = models.ForeignKey(User, blank=True, null=True)

	username_nonregistered = models.CharField(max_length=30, blank=True)   # for non-registered users
	user_email_nonregistered = models.CharField(max_length=50, blank=True)  # for non-registered users
	confirmed_email_nonregistered = models.BooleanField(default=False, blank=True) # for non-registered users
	
	date_posted = models.DateTimeField(auto_now=True)
	drafts = models.ManyToManyField(Uploaded_image, related_name="drafts", blank=True, null=True)
	gift_info = models.CharField(max_length=1000)
	gift_image = models.OneToOneField(Uploaded_image, blank=True, null=True) #models.FileField(upload_to="Gift_images", blank=True)
	designer = models.ForeignKey(User, related_name="designer", blank=True, null=True) 
	bidding_designers = models.ManyToManyField(User, related_name="bidding_designers", blank=True)
	request_mode = models.SmallIntegerField(blank=True, null=True) # "1": first come first serve "2": bidding	
	accepted = models.BooleanField(default=False) 
	date_accepted = models.DateTimeField(blank=True, null=True)
	liked = models.ManyToManyField(User, related_name="liked_posts", blank=True, null=True) 
	tags = models.ManyToManyField(Tag, related_name="tagged_posts", blank=True, null=True) 
	date_final_design_accepted = models.DateTimeField(blank=True, null=True)	
	gift_received = models.BooleanField(default=False) 

	def __unicode__(self):
		return self.text

class Design_Response(models.Model):
	design_uploaded = models.BooleanField(default=False)
	design_pictures = models.ManyToManyField(Uploaded_image, related_name="design_pictures", blank=True, null=True) 
	design_liked = models.ManyToManyField(User, related_name="liked_designs", blank=True, null=True) 
	design_description = models.CharField(max_length=5000) 
	date_completed = models.DateTimeField(blank=True, null=True)	
	design_request = models.OneToOneField(Design_Request)

	def __unicode__(self):
		return self.design_description


class UserProfile(models.Model):
	user = models.OneToOneField(User) 
	role = models.SmallIntegerField(default=3) # "1": design seeker "2": designer "3": others
	profile_image = models.FileField(upload_to="media", blank=True, null=True)
	image_type = models.CharField(max_length=50)
	age = models.IntegerField(default = 20)   
	school = models.CharField(max_length=50, blank=True)
	interests = models.ManyToManyField(Tag, related_name="interested_users", blank=True, null=True) 
	bio = models.CharField(max_length=2000, blank=True)
	friends = models.ManyToManyField(User, related_name="friends", blank=True, null=True)

def __unicode__(self):
	return self.username
	

class Comment(models.Model):
	text = models.CharField(max_length=800)
	user = models.ForeignKey(User, blank=True, null=True)
	username = models.CharField(max_length=30)  #for non-registered users
	date_posted = models.DateTimeField(auto_now=True)
	attached_images = models.ManyToManyField(Uploaded_image, related_name="original_post", blank=True, null=True)
	design_Request = models.ForeignKey(Design_Request, related_name="comments") 
	liked = models.ManyToManyField(User, related_name="liked_comments", blank=True, null=True)

	def __unicode__(self):
		return self.text


class Message(models.Model):
	sender = models.ForeignKey(User, related_name = 'message_sender')
	recipient = models.ForeignKey(User, related_name = 'message_recipient')
	subject = models.CharField(max_length = 256)
	content = models.CharField(max_length = 2048)
	time_stamp = models.DateTimeField(default = datetime.now)
	have_read = models.NullBooleanField(default = False)
	message_pic = models.ImageField(upload_to="media", blank=True, null=True)
	def __unicode__(self):
		return self.id

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.core.exceptions import *
# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from datetime import datetime

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Import CoDEX models and forms
from CoDEX.models import *
from CoDEX.forms import AddPost, EditDesignResponse
# Used to send mail from within Django
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

MAX_UPLOAD_SIZE = 2500000

def set_template_current_status(request):
	# Decide which template to extend according to the user login status
	if request.user.is_authenticated():
		if request.user.userprofile.role == 1:
			template_current_status = 'CoDEX/seeker.html' 
		else:
			if request.user.userprofile.role == 2:
				template_current_status = 'CoDEX/designer.html' 
			else:
				template_current_status = 'CoDEX/seeker.html' 
	else:
		template_current_status = 'CoDEX/guest.html' 
	return template_current_status

@login_required
@transaction.atomic
def add_post(request):
	context = {}
	# Decide which template to extend according to the user login status
	template_current_status = set_template_current_status(request)  
	context['template_current_status'] = template_current_status
	
	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = AddPost()
		context['status'] = 'get'
		return render(request, 'CoDEX/post_request.html', context)

	form = AddPost(request.POST, request.FILES)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		posts =  Design_Request.objects.order_by('-date_posted')       
		return render(request, 'CoDEX/post_request.html', context)

	if request.user.is_authenticated():
		new_post = Design_Request(title=form.cleaned_data['title'], 
									text=form.cleaned_data['text'], 
									gift_info = form.cleaned_data['gift_info'], 
									user=request.user, 
									) 
	else:
		new_post = Design_Request(title=form.cleaned_data['title'], 
									text=form.cleaned_data['text'], 
									gift_info = form.cleaned_data['gift_info'], 
									#username_nonregistered = models.CharField(max_length=30, blank=True),   # for non-registered users
									#user_email_nonregistered = models.CharField(max_length=50, blank=True),  # for non-registered users
									)
	new_post.save()

	# Add tags
	for tag in form.cleaned_data['tags']:
		new_post.tags.add(tag)
		tag.num_posts = tag.num_posts + 1
		tag.save()

	# Add request mode
	new_post.request_mode = form.cleaned_data['request_mode']

	if 'uploaded_image' in request.FILES:
		if not request.FILES['uploaded_image'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['uploaded_image'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['uploaded_image'],
									image_type=request.FILES['uploaded_image'].content_type)	
			image.save()
			new_post.drafts.add(image)
	if 'uploaded_image2' in request.FILES:
		if not request.FILES['uploaded_image2'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['uploaded_image2'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['uploaded_image2'],
									image_type=request.FILES['uploaded_image2'].content_type)	
			image.save()
			new_post.drafts.add(image)
	if 'uploaded_image3' in request.FILES:
		if not request.FILES['uploaded_image3'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['uploaded_image3'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['uploaded_image3'],
									image_type=request.FILES['uploaded_image3'].content_type)	
			image.save()
			new_post.drafts.add(image)
	if 'uploaded_image4' in request.FILES:
		if not request.FILES['uploaded_image4'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['uploaded_image4'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['uploaded_image4'],
									image_type=request.FILES['uploaded_image4'].content_type)	
			image.save()
			new_post.drafts.add(image)
	if 'uploaded_image5' in request.FILES:
		if not request.FILES['uploaded_image5'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['uploaded_image5'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['uploaded_image5'],
									image_type=request.FILES['uploaded_image5'].content_type)	
			image.save()
			new_post.drafts.add(image)
	if 'gift_image' in request.FILES:
		if not request.FILES['gift_image'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['gift_image'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['gift_image'],
									image_type=request.FILES['gift_image'].content_type)	
			image.save()
			new_post.gift_image = image

	new_post.save()
	return redirect('/design_market')
	#return render(request, 'CoDEX/post_request.html', context)

def view_post(request, post_id):
	context = {}
	context = pirvate_view_post(request, post_id) 
	template_current_status = set_template_current_status(request)	
	context['template_current_status'] = template_current_status
	try:   	
		post = Design_Request.objects.get(id = post_id)
		users = post.liked.all()
		if request.user in users:
			context['liked'] = 1
		else:
			context['liked'] = 0
	except ObjectDoesNotExist:
		raise Http404    
	return render(request, 'CoDEX/post.html', context) #HttpResponse(drafts_url, content_type='text') 

@login_required
def accept_request(request):
	template_current_status = set_template_current_status(request)
	post_id = request.POST['post_id']
	# Check if the user is a designer 
	if not request.user.userprofile.role == 2:
		context = pirvate_view_post(request, post_id) 
		context['template_current_status'] = template_current_status
		context['message'] = "You are not a designer (yet!). You can change it in Edit Profile page."
		return render(request, 'CoDEX/post.html', context) #HttpResponse(drafts_url, content_type='text') 
	# The user is a designer
	else: 
		try:
			post = Design_Request.objects.get(id=post_id)
			# If the request is a bidding request
			if post.request_mode == 2:
				post.bidding_designers.add(request.user)
				post.save()
			# All other cases are considered first come first serve...
			else:
				post.designer = request.user
				post.accepted = True
				post.save()

				email_body = request.user.username + " has accepted your design request! Check out his/her profile <a href='http://%s%s'>now</a>." % (request.get_host(), reverse('view_profile', kwargs={'id':request.user.id}))
				send_mail(subject="Someone has just accepted your design request!",
				message= email_body,
				html_message= email_body,
				from_email="no-reply@CoDEX.com",
				recipient_list=[post.user.email])


				# Create a design response object immediately
				design_response = Design_Response(design_description = "I'm working on it. Sit back.",
										design_request = post,
										date_completed = datetime.now())
				design_response.save()
			# Re render the page with a message
			context = pirvate_view_post(request, post_id) 
			context['template_current_status'] = template_current_status
			context['message'] = "Hooray! You successfully accepted the request!"			
			return render(request, 'CoDEX/post.html', context)
		except ObjectDoesNotExist:
			context = pirvate_view_post(request, post_id) 
			context['template_current_status'] = template_current_status
			context['message']='Post Not Found!!'
			return render(request, 'CoDEX/post.html', context)

@login_required
def edit_response(request):
	context = {}
	# Decide which template to extend according to the user login status
	template_current_status = set_template_current_status(request)  
	context['template_current_status'] = template_current_status
	
	# Just display the post page if this is a GET request.
	#if request.method == 'GET':
	#	view_post(request, request.POST.get('post_id', False)

	# Retrieve the design response, if the user goes here accidentally, he will
	# be redirected home
	id=request.POST.get('post_id',False)
	if not id:
		context['message'] = "You can't edit this design response."
		posts =  Design_Request.objects.order_by('-date_posted')
		context['posts'] = posts
		if request.user.is_authenticated():
			nowuser = request.user 
			context['nowuser'] = nowuser

		return render(request, 'CoDEX/design_market.html', context)

	post = Design_Request.objects.get(id=id)
	design_response = Design_Response.objects.get(design_request=post)

	form = EditDesignResponse()
	context['form'] = form
	context['design_description'] = design_response.design_description
	context['design_response'] = design_response
	if design_response.design_pictures.all().count()>0:
		designs = design_response.design_pictures.all()
		designs_id = []
		for img in designs:
			designs_id.append(img.id)
		context['designs_id']=designs_id

	return render(request, 'CoDEX/edit_response.html', context)

@login_required
def submit_response(request):
	context = {}
	# Decide which template to extend according to the user login status
	template_current_status = set_template_current_status(request)  
	context['template_current_status'] = template_current_status
	
	# Retrieve the design response, if the user goes here accidentally, he will
	# be redirected home
	id=request.POST.get('post_id',False)
	if not id:
		context['message'] = "You can't edit this design response."
		posts =  Design_Request.objects.order_by('-date_posted')
		context['posts'] = posts 
		if request.user.is_authenticated():
			nowuser = request.user 
			context['nowuser'] = nowuser
		return render(request, 'CoDEX/design_market.html', context)

	# Get the form data
	post = Design_Request.objects.get(id=id)
	design_response = Design_Response.objects.get(design_request=post)
	context['design_response'] = design_response

	design_form = EditDesignResponse(request.POST, request.FILES)
	context['form'] = design_form

	# Validates the form.
	if not design_form.is_valid():
		context['message']="Invalid form."
		return render(request, 'CoDEX/edit_response.html', context)

	# Update design description and date_completed in the post
	post.date_completed = datetime.now()
	post.save()
	design_response.design_description = design_form.cleaned_data['design_description']

	# Check uploaded design pictures
	if 'designs' in request.FILES:
		if not request.FILES['designs'].content_type.startswith('image'):
			context['message']="Please only upload images."
		elif request.FILES['designs'].size>MAX_UPLOAD_SIZE:
			context['message']="File size should not exceed 2MB."
		else:
			image = Uploaded_image(image=request.FILES['designs'],
									image_type=request.FILES['designs'].content_type)	
			image.save()
		design_response.design_pictures.add(image)
	design_response.design_uploaded = True
	design_response.save()

	context['design_response'] = design_response

	return redirect('view_post', design_response.design_request.id)
	
def add_comment(request):
	errors = []
	# Creates a new item if it is present as a parameter in the request
	if not 'comment' in request.POST or not request.POST['comment']:
		errors.append('You must say something to add a comment.')
		context = {'error': errors}
	else:
		if (request.POST['comment'].__len__()>300):
			errors.append('The comment should not exceed 300 chars.')
			context = {'error': errors}
		else:
			post_id = request.POST['post_id']
			default_image = True
			post = get_object_or_404(Design_Request,id=post_id)
			# The case the user is logged in
			if request.user.is_authenticated():
				new_comment = Comment(text=request.POST['comment'], user=request.user, username=request.user.username, date_posted=datetime.utcnow(), design_Request=post)    
			else: # The un-logged-r  in case
				new_comment = Comment(text=request.POST['comment'], username=request.POST['username'], date_posted=datetime.utcnow(), design_Request=post)
			new_comment.save() 

			context = {'comment': new_comment}
	return HttpResponse(context, content_type='text')

def update_comment(request):
	post_id = request.POST['post_id']
	last_comment_id = int(request.POST['last_comment_id'])
	comments_to_update = Comment.objects.filter(design_Request__id=post_id).filter(id__gt = int(last_comment_id)).order_by('date_posted')
	#comments_to_update = sorted(comments_to_update, key=lambda comments_to_update: comments_to_update.id, reverse = True)
	response_data = []
	for comment in comments_to_update:
		comment_json = {}
		comment_json['id'] = comment.id
		comment_json['text'] = comment.text
		if comment.user:
			comment_json['user'] = comment.user.id
		comment_json['username'] = comment.username
		comment_json['date_posted'] = comment.date_posted
		if comment.user and comment.user.userprofile.profile_image:
				comment_json['profile_image'] = comment.user.id
		else:
			comment_json['profile_image'] = 0;
		#entry_name = 'comment' + str(last_comment_id)
		last_comment_id = last_comment_id + 1
		response_data.append(comment_json);
	return JsonResponse(response_data,safe=False)

@login_required
@transaction.atomic
def delete_like(request, id):
	context = {}
	context = pirvate_view_post(request, id)
	template_current_status = set_template_current_status(request)	
	context['template_current_status'] = template_current_status

	try:   	
		post = Design_Request.objects.get(id=id)
		users = post.liked.all()

		if request.method == 'GET':
			if request.user in users:
				context['liked'] = 1
			else:
				context['liked'] = 0
			return render(request, 'CoDEX/post.html', context)

		if request.user in users:
		   post.liked.remove(request.user)
		   context['liked'] = 0
		else:
		   context['liked'] = 0
	except ObjectDoesNotExist:
		raise Http404    

	return render(request, 'CoDEX/post.html', context)

@login_required
@transaction.atomic
def like_post(request, id):
	context = {}
	context = pirvate_view_post(request, id)
	template_current_status = set_template_current_status(request)	
	context['template_current_status'] = template_current_status

	try:
		post = Design_Request.objects.get(id=id)
		users = post.liked.all()

		if request.method == 'GET':
		    if request.user in users:
			   context['liked'] = 1
		    else:
			    context['liked'] = 0
		    return render(request, 'CoDEX/post.html', context)

		if request.user not in users:
		   post.liked.add(request.user)
		   context['liked'] = 1
		else:
		    context['liked'] = 1
	except ObjectDoesNotExist:
		raise Http404
	
	return render(request, 'CoDEX/post.html', context)


def pirvate_view_post(request, post_id):
	context = {}
	try:
		# Retrieve the original post
		post = Design_Request.objects.get(id=post_id)
		context['post'] = post;
		if post.drafts.all().count()>0:
			drafts = post.drafts.all()
			drafts_id = []
			for img in drafts:
				drafts_id.append(img.id)
			context['drafts_id']=drafts_id
		if post.gift_image:
			gift_image = post.gift_image
			context['gift_image_id']=gift_image.id
		comments = Comment.objects.filter(design_Request__id=post_id).order_by('-date_posted')
		context['comments'] = comments
	except ObjectDoesNotExist:
		context['message']='Post Not Found!!'
		return context

	try:	
		# Retrieve the design response
		design_response = post.design_response
		if design_response.design_pictures.all().count()>0:
			designs = design_response.design_pictures.all()
			designs_id = []
			for img in designs:
				designs_id.append(img.id)
			context['designs_id']=designs_id
		return context
	except ObjectDoesNotExist:
		return context

@login_required
def accept_design(request):
	template_current_status = set_template_current_status(request)
	post_id = request.POST['post_id']
	try:
		post = Design_Request.objects.get(id=post_id)
		# See if the request.user is the poster
		if not request.user == post.user:
			context['message'] = "You can't do this! How did you get here?"
			return render(request, 'CoDEX/post.html', context)
		else:
			# Set design accepted date
			post.date_final_design_accepted=datetime.now()
			post.save()
			context = pirvate_view_post(request, post_id) 
			context['template_current_status'] = template_current_status
			context['message'] = "Design Accepted! Your contact information is now accessible for the designer to set up a offline communication! Get your gift prepared!"
			return render(request, 'CoDEX/post.html', context)
	except ObjectDoesNotExist:
		context = pirvate_view_post(request, post_id) 
		context['template_current_status'] = template_current_status
		context['message']='Post Not Found!!'
		return render(request, 'CoDEX/post.html', context)

@login_required
def confirm_gift(request):
	template_current_status = set_template_current_status(request)
	post_id = request.POST['post_id']
	try:
		post = Design_Request.objects.get(id=post_id)
		# See if the request.user is the poster
		if not request.user == post.designer:
			context = pirvate_view_post(request, post_id) 
			context['template_current_status'] = template_current_status
			context['message'] = "You can't do this! How did you get here?"
			return render(request, 'CoDEX/post.html', context)
		else:
			# Set design accepted date
			post.gift_received=True
			post.save()
			context = pirvate_view_post(request, post_id) 
			context['template_current_status'] = template_current_status
			context['message'] = "OK. Now everything is done :) Go find your next request if you enjoyed it."
			return render(request, 'CoDEX/post.html', context)
	except ObjectDoesNotExist:
		context = pirvate_view_post(request, post_id) 
		context['template_current_status'] = template_current_status
		context['message']='Post Not Found!!'
		return render(request, 'CoDEX/post.html', context)

@login_required
def select_designer(request):
	template_current_status = set_template_current_status(request)
	post_id = request.POST['post_id']

	designer_id = request.POST['selected_designer']
	designer = get_object_or_404(User,id=designer_id)
	post = get_object_or_404(Design_Request,id=post_id)
	post.designer = designer
	post.save()
	context = pirvate_view_post(request, post_id) 
	context['template_current_status'] = template_current_status
	return render(request, 'CoDEX/post.html', context)
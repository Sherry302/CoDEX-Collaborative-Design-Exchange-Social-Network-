from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.files import File
from django.core import serializers
from django.http import HttpResponse, Http404
from django.db.models import Q
#from fandjango.decorators import facebook_authorization_required
import json
import time
from random import randint

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Import CoDEX models and forms
from CoDEX.models import *
from CoDEX.forms import *

# Import admin functions like adding tags
from CoDEX.adminfun import *

from django.db import models
from datetime import datetime

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

from CoDEX.friends import *
from CoDEX.tag import *
from CoDEX.designRequestHandling import *


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
def home(request):
	if not hasattr(request.user, 'userprofile'):
		ran = randint(0,20000)
		new_user = User.objects.create_user(username= 'facebookuser' + str(ran), 
			password='facebook',
			email='facebookuser@fb.com')
		new_user.is_active = False
		new_user.save()
	
		user_profile = UserProfile(
			school='CMU',
			user=new_user)
		user_profile.save()

		logout(request)
		user = authenticate(username=new_user.username, password='facebook')
		login(request, user)
		
		posts =  Design_Request.objects.filter(user=request.user).order_by('-date_posted')
		posts_ifmod3 = len(posts) % 3  
		context = {'template_current_status': 'CoDEX/seeker.html', 
						'posts': posts,
						'addRow': "<div class='row'>",
						'posts_ifmod3': posts_ifmod3,
						}    
		return render(request, 'CoDEX/homepage-seeker.html', context)


	template_current_status = set_template_current_status(request)
	# Decide if the user is logged in
	if request.user.is_authenticated():
		# Decide if the logged-in user is the design seeker or designer
		if request.user.userprofile.role == 1:
			# Case for Seeker
			posts =  Design_Request.objects.filter(user=request.user).order_by('-date_posted')
			posts_ifmod3 = len(posts) % 3 # For dividing rows....
			context = {'template_current_status': template_current_status, 
						'posts': posts,
						'addRow': "<div class='row'>",
						'posts_ifmod3': posts_ifmod3,
						}    
			return render(request, 'CoDEX/homepage-seeker.html', context)
		else:
			if request.user.userprofile.role == 2:
				# Case for Designer
				# Friends posts
				friends_posts =  Design_Request.objects.filter(user__userprofile__friends=request.user).order_by('-date_posted')
				friends_posts_ifmod3 = len(friends_posts) % 3
				context = {'template_current_status': template_current_status, 
							'friends_posts': friends_posts,
							'addRow': "<div class='row'>",
							'friends_posts_ifmod3': friends_posts_ifmod3,
							}    
				# Requests I accepted
				accepted_requests =  Design_Request.objects.filter(designer=request.user).order_by('-date_posted')
				accepted_requests_ifmod3 = len(accepted_requests) % 3
				context['accepted_requests'] = accepted_requests
				context['accepted_requests_ifmod3'] = accepted_requests_ifmod3
				# Designer's interests
				interests = []
				interested_posts = []
				for item in request.user.userprofile.interests.all():
					interests.append(item.name)
					tagged_posts = Design_Request.objects.filter(tags=item).order_by('-date_posted')
					interested_posts.append(tagged_posts)
				interested_posts_ifmod3 = len(interested_posts) % 3
				context['interests'] = interests
				context['interested_posts'] = interested_posts
				context['interested_posts_ifmod3'] = interested_posts_ifmod3
				return render(request, 'CoDEX/homepage-designer.html', context)
			else: 
				posts =  Design_Request.objects.all().order_by('-date_posted')
				posts_ifmod3 = len(posts) % 3
				context = {'template_current_status': template_current_status, 
							'posts': posts,
							'addRow': "<div class='row'>",
							'posts_ifmod3': posts_ifmod3,
							}  
				return render	(request, 'CoDEX/homepage.html', context)
	else:
		posts =  Design_Request.objects.all().order_by('-date_posted')
		posts_ifmod3 = len(posts) % 3
	context = {'template_current_status': template_current_status, 
				'posts': posts,
				'addRow': "<div class='row'>",
				'posts_ifmod3': posts_ifmod3,
				}   
	return render(request, 'CoDEX/homepage.html', context)

@transaction.atomic
def register(request):
	context = {'template_current_status': 'CoDEX/guest.html'}
	context['status'] = 'NONE'

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		context['status'] = 'get'
		return render(request, 'CoDEX/register.html', context)

	# Creates a bound form from the request POST parameters and makes the 
	# form available in the request context dictionary.
	form = RegistrationForm(request.POST)
	context['form'] = form
	
	# Validates the form.
	if not form.is_valid():
		context['status'] = 'not valid'
		return render(request, 'CoDEX/register.html', context)

	# At this point, the form data is valid.  Register and login the user.
	new_user = User.objects.create_user(username=form.cleaned_data['username'], 
		password=form.cleaned_data['password1'],
		first_name=form.cleaned_data['first_name'],
		last_name=form.cleaned_data['last_name'],
		email=form.cleaned_data['email'])

	# Mark the user as inactive to prevent login before email confirmation.
	new_user.is_active = False
	new_user.save()
	user_profile = UserProfile(
		role = request.POST.get("role"),
		school=form.cleaned_data['school'],
		#interests=form.cleaned_data['interests'],
		bio=form.cleaned_data['bio'], 
		age=form.cleaned_data['age'],
		user=new_user)
	user_profile.save()
	for interest in form.cleaned_data['interests']:
		user_profile.interests.add(interest)
	user_profile.save()

	# Generate a one-time use token and an email message body
	token = default_token_generator.make_token(new_user)

	email_body = """
Welcome to CoDEX (Collaborative Design Exchange)!  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
		reverse('confirm', args=(new_user.username, token)))

	send_mail(subject="Verify your email address",
		message= email_body,
		from_email="no-reply@CoDEX.com",
		recipient_list=[new_user.email])

	context['email'] = form.cleaned_data['email']
	context['status'] = 'Registered'
	return render(request, 'CoDEX/needs-confirmation.html', context)

def design_market(request):
	template_current_status = set_template_current_status(request) 	
	posts =  Design_Request.objects.order_by('-date_posted')
	posts = get_friend_list_for_posts(request.user,posts)
	context = {'template_current_status': template_current_status, 
				'posts': posts,
				}   
	if request.user.is_authenticated():
		nowuser = request.user 
		context['nowuser'] = nowuser
	
	return render(request, 'CoDEX/design_market.html', context)


@transaction.atomic
def confirm_registration(request, username, token):
	user = get_object_or_404(User, username=username)

	# Send 404 error if token is invalid
	if not default_token_generator.check_token(user, token):
		raise Http404

	# Otherwise token was valid, activate the user.
	user.is_active = True
	user.save()
	return render(request, 'CoDEX/confirmed.html', {})


@login_required
@login_required
def view_profile(request, id):
	template_current_status = set_template_current_status(request)
	try:
		showEditProfileButton = False
		if User.objects.get(id=id) == request.user:
		   showEditProfileButton = True
		context = {}
		user = User.objects.get(id = id);
		profile = get_object_or_404(UserProfile, user = user)
		posts = Design_Request.objects.filter(user = User.objects.get(id=id)).order_by('-date_posted')
		context = {'profile' : profile, 'posts' : posts, 'template_current_status': template_current_status, "showEditProfileButton": showEditProfileButton}
		context['thisUser'] = user;

		# If designer, show all designs
		if profile.role == 2:
			accepted_requests = user.designer.all()
			request_names = []
			request_designs = []
			for req in accepted_requests:
				if Design_Response.objects.filter(design_request=req).count()>0:
					designs = req.design_response.design_pictures.all()
					designs_id = []
					for img in designs:
						designs_id.append(img.id)
				else:
					designs = []
				request_names.append({'title': req.title, 'post_id': req.id, 'designs': designs_id})
			
			context['request_names'] = request_names
			context['request_designs'] = request_designs
		
		return render(request, 'CoDEX/profile.html', context)
	except User.DoesNotExist:
		messages = []
		messages.append('Profile with id={0} does not exist'.format(id))
		context = { 'messages': messages, 'template_current_status': template_current_status}
		return render(request, 'CoDEX/profile.html', context)


@login_required
@transaction.atomic
def edit_profile(request, id):
	template_current_status = set_template_current_status(request)
	try:
		if request.method == 'GET': 
			profile = UserProfile.objects.get(user = User.objects.get(id=id))
			form = EditProfile(instance=profile)
			context = {'profile': profile, 'form': form, 'template_current_status': template_current_status}
			return render(request, 'CoDEX/edit_profile.html', context)
	
		profile = UserProfile.objects.select_for_update().get(id=id)
		form = EditProfile(request.POST, instance=profile)
		if not form.is_valid():
			context = {'profile': profile,'form': form, 'template_current_status': template_current_status}
			return render(request, 'CoDEX/edit_profile.html', context)

		form.save()
		context = {'form':form}
		return redirect(reverse('view_profile', kwargs={'id':id}))
	except ObjectDoesNotExist:
		messages = [] 
		#messages.append('Profile with id={0} does not exist'.format(id))
		profile = get_object_or_404(UserProfile, user = get_object_or_404(User, id=id))
		context = { 'profile': profile,'messages': messages, 'template_current_status': template_current_status}
		return render(request, 'CoDEX/profile.html', context)

@login_required
@transaction.atomic
def edit_profile_photo(request):
	profile = get_object_or_404(UserProfile, user=request.user)
	photo = ProfilePhoto(request.POST,request.FILES, instance = profile)
	if photo.is_valid():
		profile.profile_image = photo.cleaned_data['profile_image']
		profile.save()

	return redirect(reverse('view_profile', kwargs={'id':profile.user.id}))


def photo(request, id):
	profile = get_object_or_404(UserProfile, id=id)
	if not profile.profile_image:
		raise Http404
	return HttpResponse(profile.profile_image, content_type=profile.image_type)

def view_uploaded_image(request, image_id):
	uploaded_image = get_object_or_404(Uploaded_image, id=image_id)
	if not uploaded_image.image:
		raise Http404
	return HttpResponse(uploaded_image.image, content_type=uploaded_image.image_type)

@login_required
def my_message(request):
    context={}
    template_current_status = set_template_current_status(request)
    context = {'template_current_status': template_current_status}

    received_messages = Message.objects.filter(recipient = request.user).order_by('-time_stamp')
    sent_messages = Message.objects.filter(sender = request.user).order_by('-time_stamp')
    context['received_messages'] = received_messages
    context['sent_messages'] = sent_messages
    return render(request, 'CoDEX/my_message.html',context)


@login_required
def send_message(request):
    template_current_status = set_template_current_status(request)
    if request.method == 'POST':
        if 'recipient_id' in request.POST:
            recipient = get_object_or_404(User, id= request.POST['recipient_id'])
        elif 'recipient_name' in request.POST:
            recipient = get_object_or_404(User, username = request.POST['recipient_name'])
        else:
            return redirect('/')
        message = Message(sender = get_object_or_404(User, id = request.user.id), recipient = recipient, subject = request.POST['subject'], content = request.POST['content'])
        form = MessageModelForm(request.POST,request.FILES, instance=message)
        if form.is_valid():
            new_message = form.save()
            return redirect('/')
    else:
        recipient_id = request.GET.get('recipient_id', False)
        form = MessageModelForm()
        if recipient_id:
            recipient = get_object_or_404(User, id = recipient_id)
            return render(request, 'CoDEX/send_message.html', {'recipient': recipient, 'form':form, 'template_current_status': template_current_status})
        else:
            return render(request, 'CoDEX/send_message.html', {'recipient': '', 'form':form, 'template_current_status': template_current_status})


@login_required
def view_message(request):
    template_current_status = set_template_current_status(request)
    message_id = request.GET.get('message_id', False)
    if message_id:
        my_message = get_object_or_404(Message, id = message_id)
        return render(request, 'CoDEX/view_message.html', {'my_message': my_message, 'template_current_status': template_current_status})
    else:
        raise Http404


@transaction.atomic
def search(request):
    template_current_status = set_template_current_status(request)

    keyword = request.GET.get('keyword', False)  
    category = request.GET.get('category', False)
    posts_tag = []
    posts_text = []
    posts = []
    users = []
    if keyword =='':
        posts = Design_Request.objects.all()
        users = User.objects.all()
    elif category == False:
        posts_text = Design_Request.objects.filter( Q(text__icontains= keyword) | Q(title__icontains=keyword))
        tags = Tag.objects.filter(name__icontains = keyword)
        for tag in tags:
           posts_temp = tag.tagged_posts.all()
           posts_tag.extend(posts_temp)
        posts = list(set(list(posts_text) + posts_tag))
        users = User.objects.filter(Q(username__icontains= keyword))
        #users = User.objects.filter(Q(username__icontains= keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains = keyword))
    else:
        if category == 'Post Tag':
            tags = Tag.objects.filter(name__icontains = keyword)
            for tag in tags:
                posts_temp = tag.tagged_posts.all()
                posts_tag.extend(posts_temp)
            return render(request, 'CoDEX/search_results.html',{'posts': posts_tag, 
        	                                                    'users': '',
        	                                                    'keyword': keyword, 
        	                                                    'template_current_status': template_current_status})
        if category == 'Post Title and Context':
            posts_text = Design_Request.objects.filter( Q(text__icontains= keyword) | Q(title__icontains=keyword))
            return render(request, 'CoDEX/search_results.html',{'posts': posts_text,
        	                                                    'users': '',
        	                                                    'keyword': keyword, 
        	                                                    'template_current_status': template_current_status})

        if category == 'User Profile':
            users = User.objects.filter(Q(username__icontains= keyword))
            #users = User.objects.filter(Q(username__icontains= keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains = keyword))
            return render(request, 'CoDEX/search_results.html',{'posts': '', 
        	                                                    'users': users,
        	                                                    'keyword': keyword, 
        	                                                    'template_current_status': template_current_status})
          
    return render(request, 'CoDEX/search_results.html',{'posts': posts, 
        	                                            'users': users,
        	                                            'keyword': keyword, 
        	                                            'template_current_status': template_current_status})



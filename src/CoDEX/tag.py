from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
# Import CoDEX models and forms
from CoDEX.models import *
from CoDEX.forms import *

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
	
def add_default_tags(request):
	tag = Tag(name='Logo', num_posts=0)
	tag.save()
	tag = Tag(name='Web UI', num_posts=0)
	tag.save()
	tag = Tag(name='Mobile UI', num_posts=0)
	tag.save()
	tag = Tag(name='Illustration', num_posts=0)
	tag.save()
	tag = Tag(name='Photoshop', num_posts=0)
	tag.save()
	tag = Tag(name='Poster', num_posts=0)
	tag.save()
	tag = Tag(name='Graphic', num_posts=0)
	tag.save()
	tag = Tag(name='Photo', num_posts=0)
	tag.save()
	tag = Tag(name='Drawing', num_posts=0)
	tag.save()
	tag = Tag(name='Infographic', num_posts=0)
	tag.save()
	context = {'template_current_status': 'CoDEX/guest.html'}
	context['message'] = "Done creating default tags."
	return render(request, 'CoDEX/add_tag.html', context)


def add_tag(request):
	context = {'template_current_status': 'CoDEX/guest.html'}
	if request.method == 'POST':
		tag_form = AddTag(request.POST)
		if not tag_form.is_valid():
			context['form'] = tag_form
			context['message'] = 'Form Invalid.'
			return render(request, 'CoDEX/add_tag.html', context)
		tag_form.save()
		context['form'] = tag_form
		context['message'] = 'Tag Added.'
		return render(request, 'CoDEX/add_tag.html', context)
	tag_form = AddTag()
	context['form'] = tag_form
	return render(request, 'CoDEX/add_tag.html', context)

def tag_a_post(request):
	# Check if user entered anything
	if not 'tag_name' in request.POST:
		context = {'message': 'A tag name is required to tag. (of course)'}
		# Everything else for rendering the post page
		template_current_status = set_template_current_status(request)
		context['template_current_status'] = template_current_status
		try:
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
			return render(request, 'CoDEX/post.html', context) #HttpResponse(drafts_url, content_type='text') 
		except ObjectDoesNotExist:
			context['message']='Post Not Found!!'
			return render(request, 'CoDEX/post.html', context)
	# Tag is entered correctly!
	else:
		# Check if the tag already exists
		if Tag.objects.filter(name__iexact=request.POST['tag_name']).count() > 0:
			post = get_object_or_404(Design_Request, id=request.POST['post_id'])
			tag = get_object_or_404(Tag, name__iexact=request.POST['tag_name'])
			#tag = Tag.objects.get(name__iexact=request.POST['tag_name'])

			# Check if the post is already tagged with the current tag, if so, do nothing...
			if not post.tags.filter(name__iexact=tag.name).count() > 0:
				post.tags.add(tag)
				tag.num_posts = tag.num_posts + 1
				post.save()
				tag.save()
		else:
			new_tag = Tag(name=request.POST['tag_name'], num_posts=1)
			new_tag.save()
			post = get_object_or_404(Design_Request, id=request.POST['post_id'])
			post.tags.add(new_tag)
			post.save()
		return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'CoDEX/design-market'))

def add_an_interest(request):
	# Check if user entered anything
	if not 'tag_name' in request.POST:
		context = request.context
		context['message'] = "You didn't type in any interest. (That's bad)"
		# Return to the previous page
		return render(request, request.META.get('HTTP_REFERER', 'CoDEX/design-market'), context)
	# Tag is entered correctly!
	else:
		# Check if the tag already exists
		if Tag.objects.filter(name__iexact=request.POST['tag_name']).count() > 0:
			tag = get_object_or_404(Tag, name__iexact=request.POST['tag_name'])
			# Check if the post is already tagged with the current tag, if so, do nothing...
			if not request.user.userprofile.interests.filter(name__iexact=tag.name).count() > 0:
				user_profile = request.user.userprofile
				user_profile.interests.add(tag)
				user_profile.save()
		else:
			new_tag = Tag(name=request.POST['tag_name'], num_posts=1)
			new_tag.save()
			user_profile = request.user.userprofile
			user_profile.interests.add(new_tag)
			user_profile.save()
		return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'CoDEX/design-market'))

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

# Import CoDEX models and forms
from CoDEX.models import *

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

def get_friend_list_for_posts(user, posts):
	for post in posts:
		if post.user.friends.filter(id=user.id).count()>0:
			post.isFriend = True
		else:
			post.isFriend = False
	return posts

@login_required
def add_friend(request, user_id):
	user_profile = get_object_or_404(UserProfile, user = request.user)
	user = get_object_or_404(User, id=user_id)
	user_profile.friends.add(user)
	return redirect(reverse('design_market'))

@login_required
def remove_friend(request, user_id):
	user_profile = get_object_or_404(UserProfile, user = request.user)
	user = get_object_or_404(User, id=user_id)
	user_profile.friends.remove(user)
	return redirect(reverse('design_market'))
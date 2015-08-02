from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^$', 'CoDEX.views.home', name='home'),
	url(r'^register$', 'CoDEX.views.register', name='register'),
	url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'CoDEX.views.confirm_registration', name='confirm'),
	url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'CoDEX/login.html'}, name='login'),
	url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
	url(r'^design_market$', 'CoDEX.views.design_market', name = "design_market"),
	# Request related functions
	url(r'^design_market/post_request$','CoDEX.views.add_post', name = "add_post"),
	url(r'^design_market/post/(?P<post_id>\d+)$','CoDEX.views.view_post', name = "view_post"),
	url(r'^design_market/accept_post$','CoDEX.views.accept_request', name = "accept_request"),
	url(r'^design_market/select_designer$','CoDEX.views.select_designer', name = "select_designer"),
	url(r'^design_market/edit_response$','CoDEX.views.edit_response', name = "edit_response"),
	url(r'^design_market/submit_response$','CoDEX.views.submit_response', name = "submit_response"),
	url(r'^design_market/add_comment$','CoDEX.views.add_comment', name = "add_comment"),
	url(r'^design_market/update_comment$','CoDEX.views.update_comment', name = "update_comment"),
	url(r'^design_market/accept_design$','CoDEX.views.accept_design', name = "accept_design"),
	url(r'^design_market/confirm_gift$','CoDEX.views.confirm_gift', name = "confirm_gift"),
	# Profile related functions
	url(r'^profile/(?P<id>\d+)$', 'CoDEX.views.view_profile', name='view_profile'),
	url(r'^edit_profile/(?P<id>\d+)$', 'CoDEX.views.edit_profile', name='edit_profile'),
	url(r'^photo/(?P<id>\d+)$', 'CoDEX.views.photo', name='photo'),
    url(r'^edit_profile_photo$', 'CoDEX.views.edit_profile_photo', name='edit_profile_photo'),
    url(r'^uploaded_image/(?P<image_id>\d+)$', 'CoDEX.views.view_uploaded_image', name='view_uploaded_image'),
    # Friends function
    url(r'^add_friend/(?P<user_id>\d+)$', 'CoDEX.views.add_friend', name='add_friend'),
    url(r'^remove_friend/(?P<user_id>\d+)$', 'CoDEX.views.remove_friend', name='remove_friend'),
    # Tag function
    url(r'^add_tag$', 'CoDEX.views.add_tag', name='add_tag'),
    url(r'^add_default_tags$', 'CoDEX.views.add_default_tags', name='add_default_tags'),
    url(r'^tag_a_post$', 'CoDEX.views.tag_a_post', name='tag_a_post'),
    url(r'^add_an_interest$', 'CoDEX.views.add_an_interest', name='add_an_interest'),
    # Message function
    url(r'^message$', 'CoDEX.views.my_message', name='my_message'),
    url(r'^send_message$', 'CoDEX.views.send_message', name = 'send_message'),
    url(r'^view_message$', 'CoDEX.views.view_message', name='view_message'),

    url(r'^search$','CoDEX.views.search', name='search'),
    url(r'^delete_like/(?P<id>\d+)$','CoDEX.views.delete_like', name='delete_like'),
    url(r'^like_post/(?P<id>\d+)$', 'CoDEX.views.like_post', name='like_post'),
    url(r'', include('social_auth.urls')),
)   


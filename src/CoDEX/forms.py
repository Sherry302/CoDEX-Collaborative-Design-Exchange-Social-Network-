from django import forms

from django.contrib.auth.models import User
from models import *

MAX_UPLOAD_SIZE = 2500000

class RegistrationForm(forms.Form):
	username   = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
	first_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
	last_name  = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
	email = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
	age = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
	school = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
	interests = forms.ModelMultipleChoiceField(queryset=Tag.objects.exclude(id__gt=10), widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}), required=False)
	password1  = forms.CharField(max_length = 200, 
								 label='Password', 
								 widget = forms.PasswordInput(attrs={'class': 'form-control', 'rows': 1}))
	password2  = forms.CharField(max_length = 200, 
								 label='Confirm password',  
								 widget = forms.PasswordInput(attrs={'class': 'form-control', 'rows': 1}))
	bio = forms.CharField(max_length = 2000,
				  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 8}))

	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super(RegistrationForm, self).clean()

		# Confirms that the two password fields match
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords did not match.")

		# Simple check on the email address
		emailadd = cleaned_data.get('email')
		if (emailadd.find('@')==-1):
			raise forms.ValidationError("Please enter a valid Email address.")

		#if (emailadd.find('edu')==-1):
		#	raise forms.ValidationError("A '.edu' Email is required to register.")

		# We must return the cleaned data we got from our parent.
		return cleaned_data


	# Customizes form validation for the username field.
	def clean_username(self):
		# Confirms that the username is not already present in the
		# User model database.
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return username


class ViewForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = "__all__" 


class EditForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		exclude = {'user',
			   'image_type',
			   'friends'
			   }
		widgets = {
				'bio': forms.Textarea(attrs={'cols': 40, 'rows': 5}),
			}

	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean_picture(self):
		picture = self.cleaned_data['profile_image']
		
		if not picture:
			return None
			
		if not picture.content_type or not picture.content_type.startswith('image'):
			raise forms.ValidationError('File type is not image')
		if picture.size > MAX_UPLOAD_SIZE:
			raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
		return picture


class AddPost(forms.Form):
	title   = forms.CharField(max_length = 100,
								widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder':'Subject', 'name' : 'subject' }))
	text = forms.CharField(max_length=5000,
						   widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder':'Share your feeling to others ...', 'name' : 'text' }))
	gift_info = forms.CharField(max_length=1000,
						   widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder':'Share your feeling to others ...', 'name' : 'text' }))
	Drafts_or_Reference_Images = forms.FileField(required=False)
	tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.exclude(id__gt=10), widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}), required=False)
	request_mode = forms.ChoiceField(choices=((1,'First-come-first-serve',),(2,'bidding',)), widget=forms.RadioSelect)

	def clean(self):
		cleaned_data = super(AddPost, self).clean()
		title = cleaned_data.get('title')
		text = cleaned_data.get('text')
		gift_info = cleaned_data.get('gift_info')
		Drafts_or_Reference_Images = cleaned_data.get('Drafts_or_Reference_Images')
		
		if not title or len(title)==0:
			raise forms.ValidationError("Title of the post can not be empty.")

		if not text or len(text)==0:
			raise forms.ValidationError("Content of the post can not be empty.")

		if not gift_info or len(gift_info)==0:
			raise forms.ValidationError("Gift Information of the post can not be empty.")

		if len(title) > 100:
			raise forms.ValidationError("The length of post title should less than or equal to 100.")

		if len(text) > 5000:
			raise forms.ValidationError("The length of post content should less than or equal to 5000.")

		if len(gift_info) > 1000:
			raise forms.ValidationError("The length of gift information should less than or equal to 1000.")

		return cleaned_data
	
	def clean_picture(self):
		picture = self.cleaned_data['Drafts_or_Reference_Images']
		
		if not picture:
			return None
		if not picture.content_type or not picture.content_type.startswith('image'):
			raise forms.ValidationError('File type is not image')
		if picture.size > MAX_UPLOAD_SIZE:
			raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
		return picture

class EditDesignResponse(forms.Form):
	design_description = forms.CharField(max_length=5000,
						   widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder':'Share your feeling to others ...', 'name' : 'text' }))
	designs = forms.FileField(required=False)
	
	def clean(self):
		cleaned_data = super(EditDesignResponse, self).clean()
		design_description = cleaned_data.get('design_description')
		
		if not design_description or len(design_description)==0:
			raise forms.ValidationError("Design description can not be empty.")

		if len(design_description) > 5000:
			raise forms.ValidationError("The length of description should less than or equal to 5000 chars.")

		return cleaned_data
	
	def clean_picture(self):
		picture = self.cleaned_data['designs']
		if not picture:
			return None
		if not picture.content_type or not picture.content_type.startswith('image'):
			raise forms.ValidationError('File type is not image')
		if picture.size > MAX_UPLOAD_SIZE:
			raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
		return picture

class EditProfile(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = (
            'user',
            'image_type',
            'profile_image',
            'friends',
            'interests'
        )
        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user','')
            super(EditProfile, self).__init__(*args, **kwargs)
            if user:
               self.fields['email'].initial = user[0]['email']

class ProfilePhoto(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image']

    def clean_profile_image(self):
        profile_image = self.cleaned_data['profile_image']
        if not profile_image:
            return None
        if not profile_image.content_type or not profile_image.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if profile_image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return profile_image


class AddTag(forms.ModelForm):
	class Meta:
		model = Tag
		fields = "__all__" 

class MessageModelForm(forms.ModelForm):
	subject = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))
	content = forms.CharField(max_length=2048, widget=forms.Textarea(attrs={'class':'form-control'}))
	class Meta:
		model = Message
		fields = ('subject','content','message_pic')
	def clean(self):
		cleaned_data = super(MessageModelForm, self).clean()
		subject = cleaned_data.get("subject")
		if subject == '':
			self.add_error(subject, 'Subject Must Not Be Empty')


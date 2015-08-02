"""
Django settings for webProject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's0h1e0y2f8@8&0$!=yfc5rnci$wi#kfaxdoil8t$z!tv+h110m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_auth',
    'CoDEX'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
   'social_auth.backends.facebook.FacebookBackend',
   'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'webProject.urls'

# Used by the authentication system for the private-todo-list application.
# URL to use if the authentication system requires a user to log in.
LOGIN_URL = '/CoDEX/login'

# Default URL to redirect to after a user logs in.
LOGIN_REDIRECT_URL = '/CoDEX'
WSGI_APPLICATION = 'webProject.wsgi.application'

FACEBOOK_APP_ID = '970216606329397'
FACEBOOK_API_SECRET = '8b0f34c5ecbaf18d4cffd66a9005cd1b'
#FACEBOOK_EXTENDED_PERMISSIONS = [ 'public_profile', 'email','user_gender', 'user_id', 'user_first_name', 'user_last_name', 'user_bio']
FACEBOOK_EXTENDED_PERMISSIONS = ['email']
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [ ('username', 'id'),('email', 'email'),('bio','bio'),('first_name', 'first_name'),('last_name', 'last_name')]
SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'



DATABASES = {
    'default': {        
        'ENGINE': 'django.db.backends.mysql',        
        'OPTIONS': {            
         'read_default_file': '/home/ubuntu/src/database.cnf',        
        },    
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Configures Django to merely print emails rather than sending them.
# Comment out this line to enable real email-sending.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# To enable real email-sending, you should uncomment and 
# configure the settings below.

config = ConfigParser.ConfigParser()
config.read("/home/ubuntu/src/config.ini")

EMAIL_HOST = config.get('Email', 'Host')
EMAIL_PORT = config.get('Email', 'Port')
EMAIL_HOST_USER = config.get('Email', 'User')
EMAIL_HOST_PASSWORD = config.get('Email', 'Password')
EMAIL_USE_SSL = True

print 'EMAIL_HOST',EMAIL_HOST+':'+str(EMAIL_PORT)
print 'EMAIL_HOST_USER',EMAIL_HOST_USER

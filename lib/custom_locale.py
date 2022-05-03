from django.conf import settings
import uuid
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.http import HttpResponseRedirect
from django.urls import get_script_prefix, is_valid_path
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from lib.helper import get_client_ip, get_location_by_ip
#from userauth import models
import datetime
import pytz

class CustomLocaleMiddleware(MiddlewareMixin):
    """
    Custom Locale MiddleWare
    """
    response_redirect_class = HttpResponseRedirect

    def process_request(self, request):
        if request.GET.get('influencer', None):
            request.session['INFLUENCER'] = request.GET.get('influencer')
        
        custom_user_session_id = request.session.get('CUSTOM_USER_SESSION_ID', None)
        if not custom_user_session_id:
            uuid_one = str(uuid.uuid1())
            request.session['CUSTOM_USER_SESSION_ID'] = uuid_one
        lang = request.GET.get('lang', None)
        if not lang:
            lang = request.session.get('lang', None)
        country = "Italy"
        # try:
        #     resp = get_location_by_ip(get_client_ip(request))
        #     if 'country' in resp:
        #         country = resp['country']
        # except:
        #     pass
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language = is_language_prefix_patterns_used(
            urlconf)
        language = translation.get_language_from_request(
            request, check_path=i18n_patterns_used)
        language_from_path = translation.get_language_from_path(
            request.path_info)
        if not language_from_path and i18n_patterns_used and not prefixed_default_language:
            language = settings.LANGUAGE_CODE
        if country and country == 'Italy':
            language = 'it'
        if lang:
            request.session['lang'] = lang
            if lang == 'it':
                language = 'it'
                
            if lang == 'en':
                language = 'en-us'
                
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        if(request.LANGUAGE_CODE == "it"):
            request.TIME_ZONE = 'Europe/Rome'
        else:
            request.TIME_ZONE = 'America/Los_Angeles'
        # if request.session.get('ctype', None):
            # ctype = request.GET.get('ctype', None)
            # request.session['ctype'] = ctype if ctype else 'general'

    def process_response(self, request, response):
        language = translation.get_language()
        language_from_path = translation.get_language_from_path(
            request.path_info)
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language = is_language_prefix_patterns_used(
            urlconf)

        if (response.status_code == 404 and not language_from_path and
                i18n_patterns_used and prefixed_default_language):
            # Maybe the language code is missing in the URL? Try adding the
            # language prefix and redirecting to that URL.
            language_path = '/%s%s' % (language, request.path_info)
            path_valid = is_valid_path(language_path, urlconf)
            path_needs_slash = (
                not path_valid and (
                    settings.APPEND_SLASH and not language_path.endswith('/') and
                    is_valid_path('%s/' % language_path, urlconf)
                )
            )

            if path_valid or path_needs_slash:
                script_prefix = get_script_prefix()
                # Insert language after the script prefix and before the
                # rest of the URL
                language_url = request.get_full_path(force_append_slash=path_needs_slash).replace(
                    script_prefix,
                    '%s%s/' % (script_prefix, language),
                    1
                )
                return self.response_redirect_class(language_url)

        if not (i18n_patterns_used and language_from_path):
            patch_vary_headers(response, ('Accept-Language',))
        response.headers.setdefault('Content-Language', language)
        return response


# class SetLastVisitMiddleware():
#     def process_request(self, request):
#         user = request.GET.get('user',None)
#         print(user)
#         if(user):

#             if request.user.is_authenticated:
#                 # Update last visit time after request finished processing.
#                 local_tz = pytz.timezone(settings.TIME_ZONE)
#                 dt = local_tz.localize(datetime.datetime.now())
#                 models.Person.objects.filter(pk=request.user.pk).update(last_visit=dt)
#         return None

class LastVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last visit time after request finished processing.
            local_tz = pytz.timezone(settings.TIME_ZONE)
            dt = local_tz.localize(datetime.datetime.now())
            print(dt)
            #user = models.Person.objects.filter(pk=request.user.pk).update(last_visit=dt)
        response = self.get_response(request)
        return response

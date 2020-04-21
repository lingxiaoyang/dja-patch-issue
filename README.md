Two issues are noticed when PATCHing the DJA RelationshipView endpoint:

1. PATCHing the endpoint with same data as retrieved throws an IntegrityError
2. Deletion via PATCH causes the source object to be deleted, while it is expected to only delete the relationship

To replicate, run:

```bash
docker-compose up
docker-compose run web ./manage.py migrate
docker-compose run web ./manage.py shell
```

In the shell:

```python
from dja_patch_issue.models import Article, Tag
Article.objects.create()
Tag.objects.create()
```

<details>
  <summary>Proof</summary>

```
$ docker-compose run web ./manage.py shell
Python 3.8.2 (default, Apr 16 2020, 18:25:46)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from dja_patch_issue.models import Article, Tag
>>> Article.objects.create()
<Article: id=1>
>>> Tag.objects.create()
<Tag: id=1>
>>> Tag.objects.all()
<QuerySet [<Tag: id=1>]>
>>>
```
</details>


<details>
  <summary>First, GET the relationship endpoint and verify the data is empty</summary>

```
$ curl -i -X GET http://localhost:8000/articles/1/relationships/tags/
HTTP/1.1 200 OK
Date: Tue, 21 Apr 2020 14:06:36 GMT
Server: WSGIServer/0.2 CPython/3.8.2
Content-Type: application/vnd.api+json
Vary: Accept, Cookie
Allow: GET, POST, PATCH, DELETE, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 11
X-Content-Type-Options: nosniff

{"data":[]}
```
</details>

<details>
  <summary>Then, PATCH the relationship endpoint to add a relationship</summary>

```
$ curl -i -X PATCH -H "Content-Type: application/vnd.api+json" -d '{"data":[{"type": "tag", "id": "1"}]}' http://localhost:8000/articles/1/relationships/tags/
HTTP/1.1 200 OK
Date: Tue, 21 Apr 2020 14:08:22 GMT
Server: WSGIServer/0.2 CPython/3.8.2
Content-Type: application/vnd.api+json
Vary: Accept, Cookie
Allow: GET, POST, PATCH, DELETE, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 34
X-Content-Type-Options: nosniff

{"data":[{"type":"tag","id":"1"}]}
```
</details>

<details>
  <summary>Now, PATCH the relationship endpoint again with same data. The 500 IntegrityError is returned.</summary>

```
$ curl -i -X PATCH -H "Content-Type: application/vnd.api+json" -d '{"data":[{"type": "tag", "id": "1"}]}' http://localhost:8000/articles/1/relationships/tags/
HTTP/1.1 500 Internal Server Error
Date: Tue, 21 Apr 2020 14:08:45 GMT
Server: WSGIServer/0.2 CPython/3.8.2
Content-Type: text/plain; charset=utf-8
X-Frame-Options: DENY
Content-Length: 14870
Vary: Cookie
X-Content-Type-Options: nosniff

IntegrityError at /articles/1/relationships/tags/
FOREIGN KEY constraint failed

Request Method: PATCH
Request URL: http://localhost:8000/articles/1/relationships/tags/
Django Version: 3.0.5
Python Executable: /usr/local/bin/python
Python Version: 3.8.2
Python Path: ['/code', '/usr/local/lib/python38.zip', '/usr/local/lib/python3.8', '/usr/local/lib/python3.8/lib-dynload', '/usr/local/lib/python3.8/site-packages']
Server time: Tue, 21 Apr 2020 14:08:45 +0000
Installed Applications:
['django.contrib.admin',
 'django.contrib.auth',
 'django.contrib.contenttypes',
 'django.contrib.sessions',
 'django.contrib.messages',
 'django.contrib.staticfiles',
 'rest_framework',
 'dja_patch_issue']
Installed Middleware:
['django.middleware.security.SecurityMiddleware',
 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.common.CommonMiddleware',
 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware',
 'django.middleware.clickjacking.XFrameOptionsMiddleware']


Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/django/db/backends/base/base.py", line 243, in _commit
    return self.connection.commit()

The above exception (FOREIGN KEY constraint failed) was the direct cause of the following exception:
  File "/usr/local/lib/python3.8/site-packages/django/core/handlers/exception.py", line 34, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.8/site-packages/django/core/handlers/base.py", line 115, in _get_response
    response = self.process_exception_by_middleware(e, request)
  File "/usr/local/lib/python3.8/site-packages/django/core/handlers/base.py", line 113, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/usr/local/lib/python3.8/site-packages/django/views/decorators/csrf.py", line 54, in wrapped_view
    return view_func(*args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/django/views/generic/base.py", line 71, in view
    return self.dispatch(request, *args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/rest_framework/views.py", line 505, in dispatch
    response = self.handle_exception(exc)
  File "/usr/local/lib/python3.8/site-packages/rest_framework/views.py", line 465, in handle_exception
    self.raise_uncaught_exception(exc)
  File "/usr/local/lib/python3.8/site-packages/rest_framework/views.py", line 476, in raise_uncaught_exception
    raise exc
  File "/usr/local/lib/python3.8/site-packages/rest_framework/views.py", line 502, in dispatch
    response = handler(request, *args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/rest_framework_json_api/views.py", line 319, in patch
    related_instance_or_manager.add(*serializer.validated_data)
  File "/usr/local/lib/python3.8/site-packages/django/db/models/fields/related_descriptors.py", line 951, in add
    self._add_items(
  File "/usr/local/lib/python3.8/site-packages/django/db/transaction.py", line 232, in __exit__
    connection.commit()
  File "/usr/local/lib/python3.8/site-packages/django/utils/asyncio.py", line 26, in inner
    return func(*args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/django/db/backends/base/base.py", line 267, in commit
    self._commit()
  File "/usr/local/lib/python3.8/site-packages/django/db/backends/base/base.py", line 243, in _commit
    return self.connection.commit()
  File "/usr/local/lib/python3.8/site-packages/django/db/utils.py", line 90, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/usr/local/lib/python3.8/site-packages/django/db/backends/base/base.py", line 243, in _commit
    return self.connection.commit()

Exception Type: IntegrityError at /articles/1/relationships/tags/
Exception Value: FOREIGN KEY constraint failed
Request information:
USER: AnonymousUser

GET: No GET data

POST: No POST data

FILES: No FILES data

COOKIES: No cookie data

META:
CONTENT_LENGTH = '37'
CONTENT_TYPE = 'application/vnd.api+json'
DJANGO_SETTINGS_MODULE = 'dja_patch_issue.settings'
GATEWAY_INTERFACE = 'CGI/1.1'
GPG_KEY = 'E3FF2839C048B25C084DEBE9B26995E310250568'
HOME = '/root'
HOSTNAME = '19fa2b1473ac'
HTTP_ACCEPT = '*/*'
HTTP_HOST = 'localhost:8000'
HTTP_USER_AGENT = 'curl/7.64.1'
LANG = 'C.UTF-8'
PATH = '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
PATH_INFO = '/articles/1/relationships/tags/'
PYTHONUNBUFFERED = '1'
PYTHON_GET_PIP_SHA256 = '421ac1d44c0cf9730a088e337867d974b91bdce4ea2636099275071878cc189e'
PYTHON_GET_PIP_URL = 'https://github.com/pypa/get-pip/raw/d59197a3c169cef378a22428a3fa99d33e080a5d/get-pip.py'
PYTHON_PIP_VERSION = '20.0.2'
PYTHON_VERSION = '3.8.2'
QUERY_STRING = ''
REMOTE_ADDR = '172.26.0.1'
REMOTE_HOST = ''
REQUEST_METHOD = 'PATCH'
RUN_MAIN = 'true'
SCRIPT_NAME = ''
SERVER_NAME = '19fa2b1473ac'
SERVER_PORT = '8000'
SERVER_PROTOCOL = 'HTTP/1.1'
SERVER_SOFTWARE = 'WSGIServer/0.2'
TZ = 'UTC'
wsgi.errors = <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>
wsgi.file_wrapper = ''
wsgi.input = <django.core.handlers.wsgi.LimitedStream object at 0x7fbe0a1d58b0>
wsgi.multiprocess = False
wsgi.multithread = True
wsgi.run_once = False
wsgi.url_scheme = 'http'
wsgi.version = '(1, 0)'

Settings:
Using settings module dja_patch_issue.settings
ABSOLUTE_URL_OVERRIDES = {}
ADMINS = []
ALLOWED_HOSTS = []
APPEND_SLASH = True
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
AUTH_PASSWORD_VALIDATORS = '********************'
AUTH_USER_MODEL = 'auth.User'
BASE_DIR = '/code'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_KEY_PREFIX = '********************'
CACHE_MIDDLEWARE_SECONDS = 600
CSRF_COOKIE_AGE = 31449600
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = []
CSRF_USE_SESSIONS = False
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/code/db.sqlite3', 'ATOMIC_REQUESTS': False, 'AUTOCOMMIT': True, 'CONN_MAX_AGE': 0, 'OPTIONS': {}, 'TIME_ZONE': None, 'USER': '', 'PASSWORD': '********************', 'HOST': '', 'PORT': '', 'TEST': {'CHARSET': None, 'COLLATION': None, 'NAME': None, 'MIRROR': None}}}
DATABASE_ROUTERS = []
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
DATETIME_FORMAT = 'N j, Y, P'
DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S.%f', '%m/%d/%Y %H:%M', '%m/%d/%Y', '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M:%S.%f', '%m/%d/%y %H:%M', '%m/%d/%y']
DATE_FORMAT = 'N j, Y'
DATE_INPUT_FORMATS = ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d %Y', '%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y', '%B %d, %Y', '%d %B %Y', '%d %B, %Y']
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = False
DECIMAL_SEPARATOR = '.'
DEFAULT_CHARSET = 'utf-8'
DEFAULT_EXCEPTION_REPORTER_FILTER = 'django.views.debug.SafeExceptionReporterFilter'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
DEFAULT_INDEX_TABLESPACE = ''
DEFAULT_TABLESPACE = ''
DISALLOWED_USER_AGENTS = []
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = '********************'
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = '********************'
EMAIL_SUBJECT_PREFIX = '[Django] '
EMAIL_TIMEOUT = None
EMAIL_USE_LOCALTIME = False
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False
FILE_CHARSET = 'utf-8'
FILE_UPLOAD_DIRECTORY_PERMISSIONS = None
FILE_UPLOAD_HANDLERS = ['django.core.files.uploadhandler.MemoryFileUploadHandler', 'django.core.files.uploadhandler.TemporaryFileUploadHandler']
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
FILE_UPLOAD_PERMISSIONS = 420
FILE_UPLOAD_TEMP_DIR = None
FIRST_DAY_OF_WEEK = 0
FIXTURE_DIRS = []
FORCE_SCRIPT_NAME = None
FORMAT_MODULE_PATH = None
FORM_RENDERER = 'django.forms.renderers.DjangoTemplates'
IGNORABLE_404_URLS = []
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'rest_framework', 'dja_patch_issue']
INTERNAL_IPS = []
LANGUAGES = [('af', 'Afrikaans'), ('ar', 'Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('dsb', 'Lower Sorbian'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-co', 'Colombian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gd', 'Scottish Gaelic'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hsb', 'Upper Sorbian'), ('hu', 'Hungarian'), ('hy', 'Armenian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kab', 'Kabyle'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmål'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('vi', 'Vietnamese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese')]
LANGUAGES_BIDI = ['he', 'ar', 'fa', 'ur']
LANGUAGE_CODE = 'en-us'
LANGUAGE_COOKIE_AGE = None
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SAMESITE = None
LANGUAGE_COOKIE_SECURE = False
LOCALE_PATHS = []
LOGGING = {}
LOGGING_CONFIG = 'logging.config.dictConfig'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = None
MANAGERS = []
MEDIA_ROOT = ''
MEDIA_URL = ''
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
MIGRATION_MODULES = {}
MONTH_DAY_FORMAT = 'F j'
NUMBER_GROUPING = 0
PASSWORD_HASHERS = '********************'
PASSWORD_RESET_TIMEOUT_DAYS = '********************'
PREPEND_WWW = False
REST_FRAMEWORK = {'PAGE_SIZE': 10, 'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler', 'DEFAULT_PAGINATION_CLASS': 'rest_framework_json_api.pagination.JsonApiPageNumberPagination', 'DEFAULT_PARSER_CLASSES': ('rest_framework_json_api.parsers.JSONParser', 'rest_framework.parsers.FormParser', 'rest_framework.parsers.MultiPartParser'), 'DEFAULT_RENDERER_CLASSES': ('rest_framework_json_api.renderers.JSONRenderer', 'rest_framework.renderers.BrowsableAPIRenderer'), 'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata', 'DEFAULT_FILTER_BACKENDS': ('rest_framework_json_api.filters.QueryParameterValidationFilter', 'rest_framework_json_api.filters.OrderingFilter', 'rest_framework.filters.SearchFilter'), 'SEARCH_PARAM': 'filter[search]', 'TEST_REQUEST_RENDERER_CLASSES': ('rest_framework_json_api.renderers.JSONRenderer',), 'TEST_REQUEST_DEFAULT_FORMAT': 'vnd.api+json'}
ROOT_URLCONF = 'dja_patch_issue.urls'
SECRET_KEY = '********************'
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_SECONDS = 0
SECURE_PROXY_SSL_HEADER = None
SECURE_REDIRECT_EXEMPT = []
SECURE_REFERRER_POLICY = None
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = False
SERVER_EMAIL = 'root@localhost'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_FILE_PATH = None
SESSION_SAVE_EVERY_REQUEST = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SETTINGS_MODULE = 'dja_patch_issue.settings'
SHORT_DATETIME_FORMAT = 'm/d/Y P'
SHORT_DATE_FORMAT = 'm/d/Y'
SIGNING_BACKEND = 'django.core.signing.TimestampSigner'
SILENCED_SYSTEM_CHECKS = []
STATICFILES_DIRS = []
STATICFILES_FINDERS = ['django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_ROOT = None
STATIC_URL = '/static/'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
TEST_NON_SERIALIZED_APPS = []
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
THOUSAND_SEPARATOR = ','
TIME_FORMAT = 'P'
TIME_INPUT_FORMATS = ['%H:%M:%S', '%H:%M:%S.%f', '%H:%M']
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = False
USE_TZ = True
USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False
WSGI_APPLICATION = 'dja_patch_issue.wsgi.application'
X_FRAME_OPTIONS = 'DENY'
YEAR_MONTH_FORMAT = 'F Y'


You're seeing this error because you have DEBUG = True in your
Django settings file. Change that to False, and Django will
display a standard page generated by the handler for this status code.
```
</details>

<details>
  <summary>Then, PATCH the endpoint with empty data. It says the relationship is cleared.</summary>

```
$ curl -i -X PATCH -H "Content-Type: application/vnd.api+json" -d '{"data":[]}' http://localhost:8000/articles/1/relationships/tags/
HTTP/1.1 200 OK
Date: Tue, 21 Apr 2020 14:10:16 GMT
Server: WSGIServer/0.2 CPython/3.8.2
Content-Type: application/vnd.api+json
Vary: Accept, Cookie
Allow: GET, POST, PATCH, DELETE, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 11
X-Content-Type-Options: nosniff

{"data":[]}
```

</details>

<details>
  <summary>However, the related object itself was just incorrectly deleted. The database query returns nothing.</summary>

```
$ docker-compose run web ./manage.py shell
Python 3.8.2 (default, Apr 16 2020, 18:25:46)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from dja_patch_issue.models import Article, Tag
>>> Tag.objects.all()
<QuerySet []>
>>>
```
</details>

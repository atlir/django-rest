import json
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import login
from django.utils.timezone import now, timedelta
from django.shortcuts import render
import datetime
from googleapiclient.http import BatchHttpRequest
from rest_framework import permissions
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauthlib.common import generate_token
from social.apps.django_app.utils import psa
import httplib2
from oauth2client.client import AccessTokenCredentials
from apiclient import discovery
import email
import email.header
def index(request):
    return render(request, 'index.html')

@csrf_exempt
@psa('social:complete')
def register_by_access_token(request, backend):
    token = request.POST.get('access_token') or json.loads(request.body.decode('utf-8')).get('access_token')
    user = request.backend.do_auth(token)
    if user:
        login(request, user)
        response = get_access_token(user)
        return response
    else:
        response = HttpResponse("error")
        return response

@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
@permission_classes([permissions.IsAuthenticated])
def emails(request):
    credentials = AccessTokenCredentials(request.user.social_auth.get(provider="google-plus").extra_data.get('access_token'), 'gmail')
    gapi = discovery.build('gmail', 'v1', http=credentials.authorize(httplib2.Http()))
    threads = getThreads(gapi, settings.PER_PAGE, '!in:chats', request.GET.get('nextPageToken'))
    rthreads = []
    result = {}
    for thread in threads.get('threadList'):
        msg = thread['messages'][0]['payload']
        rthread = {}
        rthread['emails'] = []
        for header in msg['headers']:
            if header['name'] == 'Subject':
                rthread['subject'] = header['value']
                break
        for message in thread['messages']:
            mail = {}
            mail['snippet'] = message.get('snippet')
            for head in message.get('payload').get('headers'):
                if (head.get('name') == 'Subject'):
                    mail['subject'] = head.get('value')
                elif (head.get('name') == 'From'):
                    mail['from'] = head.get('value')
                elif (head.get('name') == 'To'):
                    mail['to'] = head.get('value')
                elif (head.get('name') == 'Date'):
                    date_tuple = email.utils.parsedate_tz(head.get('value'))
                    if date_tuple:
                        local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                        mail['date'] = '{:%d %b %Y %H:%M}'.format(local_date)
            rthread['emails'].append(mail)
        rthreads.append(rthread)

    result['threads'] = rthreads
    if 'nextPageToken' in threads['threads']:
        result['nextPageToken'] = threads['threads']['nextPageToken']

    return JsonResponse(result)


def getThreads(service, maxResults, q, nextPageToken):

    threadList = []

    def threadCallback(request_id, response, exception):
        threadList.append(response)

    batch = BatchHttpRequest()

    threads = service.users().threads().list(userId='me', maxResults=maxResults, q=q, pageToken=nextPageToken).execute()

    if 'threads' in threads:
        for thread in threads['threads']:
            batch.add(service.users().threads().get(userId='me', id=thread['id'], format='metadata', metadataHeaders=['subject','date','to','from']), callback=threadCallback)
        batch.execute()

    return {'threadList': threadList, 'threads': threads}


def get_token_json(access_token, user):
    token = {
        'access_token': access_token.token,
        'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        'token_type': 'Bearer',
        'refresh_token': access_token.refresh_token.token,
        'scope': access_token.scope,
        'user': user.username,
        'username': user.first_name + ' ' + user.last_name
    }
    return JsonResponse(token)


def get_access_token(user):
    app = Application.objects.get(name=settings.APP_NAME)

    try:
        old_access_token = AccessToken.objects.get(
            user=user,
            application=app
        )
        old_refresh_token = RefreshToken.objects.get(
            user=user,
            access_token=old_access_token
        )
    except:
        pass
    else:
        old_access_token.delete()
        old_refresh_token.delete()

    token = generate_token()

    refresh_token = generate_token()

    expires = now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    scope = "read write"

    access_token = AccessToken.objects.create(
        user=user,
        application=app,
        expires=expires,
        token=token,
        scope=scope
    )

    RefreshToken.objects.create(
        user=user,
        application=app,
        token=refresh_token,
        access_token=access_token
    )

    return get_token_json(access_token, user)
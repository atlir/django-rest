from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from oauth2_provider.models import Application
class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            for user in settings.ADMINS:
                username = user[0].replace(' ', '')
                email = user[1]
                password = user[2]
                print('Creating account for %s (%s)' % (username, email))
                admin = User.objects.create_superuser(email=email, username=username, password=password)
                admin.is_active = True
                admin.is_admin = True
                admin.save()
                if Application.objects.count() == 0:
                    app = Application.objects.create(client_id='asfsdfasdf',
                                               client_type='confidential',
                                               authorization_grant_type='client-credentials',
                                               client_secret='basdyfiavsbdcaksydcbasdyfasdfykausbdf',
                                               name='Server', user=admin)
                    app.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
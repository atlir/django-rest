FROM python:3.5
 ENV PYTHONUNBUFFERED 1
 RUN apt-get update && apt-get install -y npm
 RUN npm install -g bower
 RUN ln -s /usr/bin/nodejs /usr/bin/node
 RUN mkdir /gmail
 RUN mkdir /gmail/bower
 ADD /gmail /gmail
 WORKDIR /gmail
 ADD requirements.txt /gmail/
 RUN pip3 install -r requirements.txt
 RUN ls -la
 RUN python3 manage.py migrate
 RUN python3 manage.py initapp
 RUN python3 manage.py bower_install --allow-root
 RUN python3 manage.py collectstatic --noinput


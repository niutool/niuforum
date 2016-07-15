# niuforum

A quick and simple forum which uses the Django Framework

Installation
------------
niuforum requires python3 and django 1.9

* clone the source code
```
git clone https://github.com/niutool/niuforum.git niuforum
```
* install requirements
```
pip install -r requirements.txt
```
* create database
```
python manage.py makemigrations
python manage.py migrate
```
* after that, you can run the server
```
python manage.py runserver
```

Configuration
------------
* create a super user, who can login admin page and edit database
```
python manage.py createsuperuser
```
* login http://localhost:8000/admin, follow this [video](https://www.youtube.com/watch?v=1yqKNQ3ogKQ) to set up django-allauth module
* login http://localhost:8000/, and create a new user
* initialize the forum, create default nodes and topics
```
python manage.py initforum newuser
```
* login http://localhost:8000/admin again, and you can add more sections and nodes as you wish
* Finally the niuforum is ready for use

Getting Help
------------
To get more help, please visit http://niutool.com

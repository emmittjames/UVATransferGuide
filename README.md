# [UVA Transfer Guide](https://uvatransferguide.com)

## Table of contents
* [General Info](#general-info)
* [Technologies](#technologies)
* [Cloning](#cloning)
* [Sample Images](#sample-images)
* [License](#license)

## General Info
#### Website link: [uvatransferguide.com](https://uvatransferguide.com)

This website allows transfer students to view transfer equivalencies for UVA courses that administrators have approved. It also allows transfer students to submit new transfer equivalencies which will be reviewed by an administrator.
	
## Technologies
Project created with:
* Python
* HTML
* JavaScript
* Django
* Bootstrap

Project hosted with:
* [Heroku](https://www.heroku.com) - Full-stack Django hosting & PostgreSQL database hosting

## Cloning
1. [Install](https://docs.djangoproject.com/en/4.2/intro/install/) Python and Django if you haven't already
2. Clone the repository
3. Navigate to settings.py and change the value of `SECURE_SSL_REDIRECT` to false
4. Uncomment this code in settings.py in order to use a local SQLite database:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
Then, remove this code in settings.py in order to stop using the PostgreSQL database
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('NAME'),
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASSWORD'),
        'HOST': 'ec2-3-92-151-217.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}
```
5. Set up Google OAuth by following [this guide](https://www.section.io/engineering-education/django-google-oauth/)
6. Use the following command to start the server on port 8000
   ```
   python manage.py runserver
   ````
8. Everything should be up and running on your [local host](https://localhost:8000)

## Sample Images

#### Viewing ratings on the map
<img width="1440" alt="Viewing ratings" src="https://user-images.githubusercontent.com/90576219/216737244-dd2f58f1-1dfe-47fb-bbb1-f2856571b41e.png">

#### Submitting a water fountain rating
<img width="1440" alt="Submitting rating" src="https://user-images.githubusercontent.com/90576219/216737257-750f673f-5447-4047-9f72-cd9d08849670.png">

#### Giving feedback on the site
<img width="1440" alt="Submitting feedback" src="https://user-images.githubusercontent.com/90576219/216737404-2fcf3b53-143b-4d7b-8227-9dcc17d944c9.png">

## License
Distributed under the MIT License. See ```LICENSE``` for more information

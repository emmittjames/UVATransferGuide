# [UVA Transfer Guide](https://uvatransferguide.com)

## Table of contents
* [General Info](#general-info)
* [Technologies](#technologies)
* [Cloning](#cloning)
* [Sample Images](#sample-images)

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
Then, remove this code in settings.py in order to ensure that the local database is used
```
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}
```
5. Populate the database with UVA courses from the last 4 years by running `threadsis.py`
6. Set up Google OAuth by following [this guide](https://www.section.io/engineering-education/django-google-oauth/)
7. Use the command `python manage.py runserver` to start the server on localhost with port 8000
8. Everything should be up and running on your [localhost](https://localhost:8000)

## Sample Images

#### Student searching for all UVA MATH courses with algebra in the title
<img width="1440" alt="Screenshot 2023-08-13 at 1 34 22 AM" src="https://github.com/emmittjames/UVATransferGuide/assets/90576219/2c357b3d-214e-41e8-821d-69a4cb77fe3e">

#### Student viewing all course equivalencies for a UVA course
<img width="1440" alt="Screenshot 2023-08-13 at 12 44 32 AM" src="https://github.com/emmittjames/UVATransferGuide/assets/90576219/3b0b9bbf-68b9-425f-896d-298faf0032ae">

#### Student viewing personal requests that were accepted/rejected by an admin
<img width="1440" alt="Screenshot 2023-08-13 at 12 34 45 AM" src="https://github.com/emmittjames/UVATransferGuide/assets/90576219/c2f85450-50b8-4430-9654-0d58435c7ca6">

#### Admin handling transfer request
<img width="1440" alt="Screenshot 2023-08-13 at 1 40 12 AM" src="https://github.com/emmittjames/UVATransferGuide/assets/90576219/276631fe-9f49-49b2-b204-3bc740adecba">

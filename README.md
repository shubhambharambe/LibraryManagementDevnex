# python library management system
Python DRF library management system REST API app

===============================>Instructions to Start App<============================



you need to install (
pip install django-celery-results django-celery-beat

)


1.open (Devenex-library) folder

2.open CMD in this folder 

3.write command cd (library)

4.after that write command(python manage.py createsuperuser)

5.after that you need to add username,email and password for check Django administration(Database)

6.after that  command( python manage.py runserver)

7.you got this type of link http://127.0.0.1:8000/

8.Open your browser and navigate to:

Application: http://127.0.0.1:8000/
Admin Panel: http://127.0.0.1:8000/admin/
Log in to the admin panel using the credentials of the superuser created earlier to view or manage the database tables.

9.open new terminal and hit this command <celery -A api.celery worker --loglevel=info > to start celery scheduler


================================>how to use all API's screenshots of postman API<====================





1. Send a POST request to: " http://127.0.0.1:8000/api/token" and send data in json body
     http://127.0.0.1:8000/api/token/refresh for refresh the token

2.In the JSON body, provide the credentials used for the superuser:
 {
    "username":"", 
    "password":""
}

3.The response will include the access token and refresh token:
    "access": "example ",  
    "refresh": "example"
The access token is valid for 30 minutes.
The refresh token is valid for 1 day.

4.Use the access token for authenticated API requests by adding it to the Authorization header:
    Key:Authorization: 
    value:Bearer "put token here"
5."http://127.0.0.1:8000/swagger/" hit this url to use all APIs
6.add authorization token Bearer <token>
   

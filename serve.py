# from waitress import serve
# import os, django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akshaya.settings')  # adjust if manage.py shows something different
# django.setup()

# from akshaya.wsgi import application  # match the same name here too

# serve(application, host='127.0.0.1', port=8000)
from waitress import serve
from akshaya.wsgi import application

if __name__ == "__main__":
    serve(application, host="127.0.0.1", port=8000)
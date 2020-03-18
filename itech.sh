#!/bin/bash

cd /Users/arnoldumakhihe/other_clouds/OneDrive\ -\ University\ of\ Glasgow/python_workspace/explore-scotland
source virtualenv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver